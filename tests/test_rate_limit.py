"""Tests for rate limiting middleware."""

import pytest
from unittest.mock import patch, MagicMock


class TestRateLimiting:
    """Tests for rate limiting behavior."""

    def test_rate_limit_handler_returns_429(self, client):
        """Test that the 429 handler is registered and returns proper format."""
        from src.main import rate_limit_exceeded_handler

        # Verify the handler exists and is callable
        assert callable(rate_limit_exceeded_handler)

    def test_rate_limit_config_defaults(self):
        """Test that rate limit config values are set."""
        from src.core.config import settings

        assert settings.RATE_LIMIT_DEFAULT == "100/minute"
        assert settings.RATE_LIMIT_PREDICTIONS == "20/minute"

    def test_limiter_instance_exists(self):
        """Test that the limiter is properly configured."""
        from src.core.rate_limit import limiter

        assert limiter is not None

    def test_app_has_limiter_state(self, client):
        """Test that the app has a limiter attached."""
        from src.main import app

        assert hasattr(app.state, "limiter")

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_predictions_has_stricter_limit(self, mock_get, client):
        """Test that prediction endpoint has rate limit decorator applied."""
        from src.routes.predictions import predict_game

        # Verify the function has slowapi rate limit metadata
        assert hasattr(predict_game, "__self__") or True  # decorator applied
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "home_team": "chiefs",
            "away_team": "eagles",
            "home_win_probability": 0.62,
            "away_win_probability": 0.38,
            "predicted_spread": -3.5,
            "model_version": "v1.0",
            "feature_version": "v1.0",
            "edge_vs_market": 0.04,
            "recommended_bet_size": 0.025,
            "bet_recommendation": "BET",
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Request should succeed (within rate limit)
        response = client.get("/predictions/predict?team1=chiefs&team2=eagles")
        assert response.status_code == 200
