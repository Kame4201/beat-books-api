"""Tests for CORS middleware configuration."""
import pytest
from unittest.mock import patch


class TestCORSMiddleware:
    """Tests for CORS header behavior."""

    def test_cors_headers_allowed_origin(self, client):
        """Test that CORS headers are returned for allowed origins."""
        response = client.get("/", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_cors_preflight_request(self, client):
        """Test that OPTIONS preflight requests succeed."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-API-Key",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    def test_cors_disallowed_origin(self, client):
        """Test that disallowed origins don't get CORS headers."""
        response = client.get("/", headers={"Origin": "http://evil.com"})

        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers
