"""Tests for health check endpoint."""
import pytest


class TestHealthEndpoint:
    """Tests for GET / health check."""

    def test_health_returns_200(self, client):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_health_response_body(self, client):
        """Test health response contains expected fields."""
        response = client.get("/")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "beat-books-api"

    def test_health_response_content_type(self, client):
        """Test health response is JSON."""
        response = client.get("/")
        assert "application/json" in response.headers["content-type"]

    def test_health_only_supports_get(self, client):
        """Test that non-GET methods return 405."""
        response = client.post("/")
        assert response.status_code == 405
