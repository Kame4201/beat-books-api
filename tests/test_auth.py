"""Tests for API key authentication middleware."""
import pytest
from unittest.mock import patch


class TestAPIKeyAuth:
    """Tests for API key authentication."""

    def test_health_endpoint_no_auth_required(self, client):
        """Test that health endpoint works without API key."""
        with patch("src.core.auth.settings") as mock_settings:
            mock_settings.API_KEYS = "test-key-123"
            response = client.get("/")
            assert response.status_code == 200

    def test_no_keys_configured_allows_all(self, client):
        """Test that empty API_KEYS allows all requests (dev mode)."""
        with patch("src.core.auth.settings") as mock_settings:
            mock_settings.API_KEYS = ""
            response = client.get("/teams/KC/stats?season=2024",
                                  headers={"X-API-Key": ""})
            # Should not get 401/403 — auth is disabled
            assert response.status_code != 401
            assert response.status_code != 403

    def test_missing_api_key_returns_401(self, client):
        """Test that missing X-API-Key header returns 401."""
        with patch("src.core.auth.settings") as mock_settings:
            mock_settings.API_KEYS = "valid-key-123"
            response = client.get("/teams/KC/stats?season=2024")
            assert response.status_code == 401
            data = response.json()
            assert data["error"]["code"] == "UNAUTHORIZED"
            assert "X-API-Key" in data["error"]["message"]

    def test_invalid_api_key_returns_403(self, client):
        """Test that invalid API key returns 403."""
        with patch("src.core.auth.settings") as mock_settings:
            mock_settings.API_KEYS = "valid-key-123"
            response = client.get(
                "/teams/KC/stats?season=2024",
                headers={"X-API-Key": "wrong-key"},
            )
            assert response.status_code == 403
            data = response.json()
            assert data["error"]["code"] == "FORBIDDEN"

    def test_valid_api_key_succeeds(self, client):
        """Test that valid API key allows the request through."""
        with patch("src.core.auth.settings") as mock_settings:
            mock_settings.API_KEYS = "valid-key-123,another-key"
            from unittest.mock import AsyncMock
            with patch("src.routes.stats.data_client.get", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = {"data": {"team": "KC"}}
                response = client.get(
                    "/teams/KC/stats?season=2024",
                    headers={"X-API-Key": "valid-key-123"},
                )
                assert response.status_code == 200

    def test_multiple_valid_keys(self, client):
        """Test that any of the configured keys work."""
        with patch("src.core.auth.settings") as mock_settings:
            mock_settings.API_KEYS = "key-1,key-2,key-3"
            from unittest.mock import AsyncMock
            with patch("src.routes.stats.data_client.get", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = {"data": {}}
                response = client.get(
                    "/teams/KC/stats?season=2024",
                    headers={"X-API-Key": "key-2"},
                )
                assert response.status_code == 200
