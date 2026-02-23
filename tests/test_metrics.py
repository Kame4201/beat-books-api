"""Tests for Prometheus metrics endpoint (issue #26)."""


class TestMetricsEndpoint:
    """Validate the /metrics endpoint."""

    def test_metrics_returns_200(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_returns_prometheus_format(self, client):
        response = client.get("/metrics")
        content_type = response.headers.get("content-type", "")
        assert "text/plain" in content_type or "text/plain" in response.text[:100]

    def test_metrics_contains_request_count(self, client):
        # Make a request first to generate metrics
        client.get("/")
        response = client.get("/metrics")
        body = response.text
        assert "http_requests_total" in body or "http_request_duration" in body

    def test_metrics_contains_duration_histogram(self, client):
        client.get("/")
        response = client.get("/metrics")
        body = response.text
        assert "http_request_duration" in body

    def test_metrics_has_method_label(self, client):
        client.get("/")
        response = client.get("/metrics")
        body = response.text
        assert 'method="GET"' in body

    def test_metrics_has_handler_label(self, client):
        client.get("/")
        response = client.get("/metrics")
        body = response.text
        assert 'handler="/"' in body
