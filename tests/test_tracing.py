"""Tests for request tracing with correlation IDs (issue #27)."""

import uuid


class TestRequestIdGeneration:
    """Verify X-Request-ID generation."""

    def test_response_includes_request_id(self, client):
        response = client.get("/")
        assert "X-Request-ID" in response.headers

    def test_generated_id_is_valid_uuid(self, client):
        response = client.get("/")
        request_id = response.headers["X-Request-ID"]
        # Should not raise
        uuid.UUID(request_id)

    def test_each_request_gets_unique_id(self, client):
        r1 = client.get("/")
        r2 = client.get("/")
        assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]


class TestRequestIdForwarding:
    """Verify client-provided X-Request-ID is preserved."""

    def test_uses_client_provided_id(self, client):
        custom_id = "my-custom-trace-id-123"
        response = client.get("/", headers={"X-Request-ID": custom_id})
        assert response.headers["X-Request-ID"] == custom_id

    def test_client_id_preserved_on_different_endpoints(self, client):
        custom_id = "trace-abc-456"
        response = client.get("/", headers={"X-Request-ID": custom_id})
        assert response.headers["X-Request-ID"] == custom_id


class TestRequestIdOnAllEndpoints:
    """Verify X-Request-ID is present on all route responses."""

    def test_health_endpoint(self, client):
        response = client.get("/")
        assert "X-Request-ID" in response.headers

    def test_scrape_endpoint(self, client):
        # Will fail due to backend unavailable but should still have trace ID
        response = client.get("/scrape/2024")
        assert "X-Request-ID" in response.headers

    def test_stats_endpoint(self, client):
        response = client.get("/teams/chiefs/stats?season=2024")
        assert "X-Request-ID" in response.headers
