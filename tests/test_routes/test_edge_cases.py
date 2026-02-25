"""Edge case tests for API routes."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from fastapi import HTTPException


class TestMalformedRequests:
    """Tests for malformed or unexpected requests."""

    def test_unknown_route_returns_404(self, client):
        """Test that unknown routes return 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_wrong_method_returns_405(self, client):
        """Test that wrong HTTP method returns 405."""
        response = client.post("/")
        assert response.status_code == 405

    def test_predictions_empty_team_names(self, client):
        """Test predictions with empty string team names."""
        response = client.get("/predictions/predict?team1=&team2=")
        assert response.status_code == 400

    def test_stats_season_boundary_low(self, client):
        """Test season validation at lower boundary."""
        response = client.get("/teams/KC/stats?season=1920")
        # 1920 is valid (within ge=1920)
        assert response.status_code != 422

    def test_stats_season_boundary_high(self, client):
        """Test season validation at upper boundary."""
        response = client.get("/teams/KC/stats?season=2100")
        # 2100 is valid (within le=2100)
        assert response.status_code != 422

    def test_stats_season_out_of_range(self, client):
        """Test season outside valid range."""
        response = client.get("/teams/KC/stats?season=2101")
        assert response.status_code == 422

    def test_players_limit_boundary(self, client):
        """Test players with max limit."""
        with patch("src.routes.stats.data_client.get", new_callable=AsyncMock) as mock:
            mock.return_value = {"data": [], "pagination": None}
            response = client.get("/players?season=2024&limit=200")
            assert response.status_code == 200

    def test_players_limit_over_max(self, client):
        """Test players with limit exceeding max."""
        response = client.get("/players?season=2024&limit=201")
        assert response.status_code == 422


class TestServiceErrorForwarding:
    """Tests for error handling from backend services."""

    @pytest.mark.asyncio
    async def test_data_service_500_forwarded(self, client):
        """Test that 500 from data service is forwarded."""
        with patch("src.routes.stats.data_client.get", new_callable=AsyncMock) as mock:
            mock.side_effect = HTTPException(
                status_code=500,
                detail={"error": {"code": "INTERNAL", "message": "Database error"}},
            )
            response = client.get("/teams/KC/stats?season=2024")
            assert response.status_code == 500

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_model_service_generic_error(self, mock_get, client):
        """Test handling of unexpected status code from model service."""
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_response.text = "Bad Gateway"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Gateway", request=MagicMock(), response=mock_response
        )
        mock_get.return_value = mock_response

        response = client.get("/predictions/backtest/run-123")
        assert response.status_code == 502
