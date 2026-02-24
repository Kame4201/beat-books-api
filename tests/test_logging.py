"""Tests for structured logging middleware."""
import json
import logging
import pytest


class LogCapture(logging.Handler):
    """Test handler that captures log records."""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture(autouse=True)
def capture_logs():
    """Attach a capture handler to the beat-books-api logger."""
    api_logger = logging.getLogger("beat-books-api")
    previous_level = api_logger.level
    handler = LogCapture()
    api_logger.setLevel(logging.INFO)
    api_logger.addHandler(handler)
    yield handler
    api_logger.removeHandler(handler)
    api_logger.setLevel(previous_level)


class TestRequestLoggingMiddleware:
    """Tests for request/response logging."""

    def test_request_produces_structured_log(self, client, capture_logs):
        """Test that requests produce structured log entries."""
        response = client.get("/")

        assert response.status_code == 200
        assert len(capture_logs.records) >= 1
        record = capture_logs.records[-1]
        assert hasattr(record, "extra_data")
        data = record.extra_data
        assert data["method"] == "GET"
        assert data["path"] == "/"
        assert data["status_code"] == 200
        assert "duration_ms" in data

    def test_log_includes_duration(self, client, capture_logs):
        """Test that log entries include request duration."""
        client.get("/")

        record = capture_logs.records[-1]
        assert record.extra_data["duration_ms"] >= 0

    def test_log_includes_client_ip(self, client, capture_logs):
        """Test that log entries include client IP."""
        client.get("/")

        record = capture_logs.records[-1]
        assert "client_ip" in record.extra_data

    def test_sensitive_headers_not_logged(self, client, capture_logs):
        """Test that auth headers are not included in log data."""
        client.get("/", headers={"Authorization": "Bearer secret"})

        record = capture_logs.records[-1]
        log_str = json.dumps(record.extra_data)
        assert "secret" not in log_str
        assert "Authorization" not in log_str

    def test_json_formatter_output(self):
        """Test that JSONFormatter produces valid JSON."""
        from src.core.logging import JSONFormatter

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "test message"
        assert "timestamp" in parsed
