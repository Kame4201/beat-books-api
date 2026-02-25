import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status
import httpx

SAMPLE_PREDICTION = {
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


class TestPredictEndpoint:
    """Tests for GET /predictions/predict endpoint."""

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_predict_game_success(self, mock_get, client):
        """Test successful game prediction."""
        # Mock response from beat-books-model service
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

        # Make request
        response = client.get("/predictions/predict?team1=chiefs&team2=eagles")

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["home_team"] == "chiefs"
        assert data["away_team"] == "eagles"
        assert data["home_win_probability"] == 0.62
        assert data["bet_recommendation"] == "BET"

    def test_predict_game_invalid_team1(self, client):
        """Test prediction with invalid home team name."""
        response = client.get("/predictions/predict?team1=invalid&team2=eagles")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid team name" in response.json()["detail"]

    def test_predict_game_invalid_team2(self, client):
        """Test prediction with invalid away team name."""
        response = client.get("/predictions/predict?team1=chiefs&team2=invalid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid team name" in response.json()["detail"]

    def test_predict_game_missing_team1(self, client):
        """Test prediction with missing team1 parameter."""
        response = client.get("/predictions/predict?team2=eagles")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_predict_game_missing_team2(self, client):
        """Test prediction with missing team2 parameter."""
        response = client.get("/predictions/predict?team1=chiefs")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_predict_game_service_unavailable(self, mock_get, client):
        """Test prediction when model service is unavailable."""
        mock_get.side_effect = httpx.ConnectError("Connection refused")

        response = client.get("/predictions/predict?team1=chiefs&team2=eagles")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Model service unavailable" in response.json()["detail"]

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_predict_game_service_timeout(self, mock_get, client):
        """Test prediction when model service times out."""
        mock_get.side_effect = httpx.TimeoutException("Request timeout")

        response = client.get("/predictions/predict?team1=chiefs&team2=eagles")

        assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        assert "timeout" in response.json()["detail"].lower()

    def test_predict_game_case_insensitive(self, client):
        """Test that team names are case-insensitive."""
        with patch("httpx.AsyncClient.get") as mock_get:
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

            # Test with uppercase
            response = client.get("/predictions/predict?team1=CHIEFS&team2=EAGLES")
            assert response.status_code == status.HTTP_200_OK


class TestBacktestEndpoint:
    """Tests for GET /predictions/backtest/{run_id} endpoint."""

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_get_backtest_results_success(self, mock_get, client):
        """Test successful backtest results retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "run_id": "test-run-123",
            "start_date": "2024-09-01",
            "end_date": "2024-12-31",
            "total_games": 256,
            "correct_predictions": 165,
            "accuracy": 0.644,
            "total_profit": 1250.50,
            "roi": 0.125,
            "sharpe_ratio": 1.8,
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = client.get("/predictions/backtest/test-run-123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["run_id"] == "test-run-123"
        assert data["total_games"] == 256
        assert data["accuracy"] == 0.644

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_get_backtest_results_not_found(self, mock_get, client):
        """Test backtest results retrieval when run_id doesn't exist."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=MagicMock(), response=mock_response
        )
        mock_get.return_value = mock_response

        response = client.get("/predictions/backtest/nonexistent-run")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_get_backtest_results_service_unavailable(self, mock_get, client):
        """Test backtest results when model service is unavailable."""
        mock_get.side_effect = httpx.ConnectError("Connection refused")

        response = client.get("/predictions/backtest/test-run-123")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Model service unavailable" in response.json()["detail"]


class TestModelsEndpoint:
    """Tests for GET /predictions/models endpoint."""

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_list_models_success(self, mock_get, client):
        """Test successful models list retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {
                    "model_id": "model-001",
                    "model_version": "v1.0",
                    "feature_version": "v1.0",
                    "trained_date": "2024-01-15",
                    "accuracy": 0.652,
                    "is_active": True,
                },
                {
                    "model_id": "model-002",
                    "model_version": "v1.1",
                    "feature_version": "v1.1",
                    "trained_date": "2024-02-01",
                    "accuracy": 0.668,
                    "is_active": False,
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = client.get("/predictions/models")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "models" in data
        assert len(data["models"]) == 2
        assert data["models"][0]["model_id"] == "model-001"
        assert data["models"][0]["is_active"] is True

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_list_models_empty(self, mock_get, client):
        """Test models list retrieval when no models exist."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = client.get("/predictions/models")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["models"] == []

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_list_models_service_unavailable(self, mock_get, client):
        """Test models list when model service is unavailable."""
        mock_get.side_effect = httpx.ConnectError("Connection refused")

        response = client.get("/predictions/models")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Model service unavailable" in response.json()["detail"]


class TestBatchPredictions:
    """Tests for POST /predictions/batch endpoint."""

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_batch_success(self, mock_get, client):
        """Test batch prediction with all games succeeding."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_PREDICTION
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = client.post(
            "/predictions/batch",
            json={"games": [{"team1": "chiefs", "team2": "eagles"}]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["succeeded"] == 1
        assert data["failed"] == 0
        assert data["results"][0]["prediction"] is not None

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_batch_partial_failure(self, mock_get, client):
        """Test batch with mix of valid and invalid teams."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_PREDICTION
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        response = client.post(
            "/predictions/batch",
            json={
                "games": [
                    {"team1": "chiefs", "team2": "eagles"},
                    {"team1": "invalid", "team2": "eagles"},
                ]
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["succeeded"] == 1
        assert data["failed"] == 1
        assert data["results"][0]["prediction"] is not None
        assert data["results"][1]["error"] is not None

    def test_batch_empty_input(self, client):
        """Test batch prediction with empty games list."""
        response = client.post(
            "/predictions/batch",
            json={"games": []},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["succeeded"] == 0
        assert data["failed"] == 0
        assert data["results"] == []


class TestWeekPredictions:
    """Tests for GET /predictions/week/{season}/{week} endpoint."""

    @patch("httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_week_predictions_success(self, mock_httpx_get, client):
        """Test week prediction that fetches schedule and predicts."""
        with patch(
            "src.routes.predictions.data_client.get", new_callable=AsyncMock
        ) as mock_data:
            mock_data.return_value = {
                "data": {
                    "games": [
                        {"home_team": "chiefs", "away_team": "eagles"},
                    ]
                }
            }

            predict_response = MagicMock()
            predict_response.status_code = 200
            predict_response.json.return_value = SAMPLE_PREDICTION
            predict_response.raise_for_status = MagicMock()
            mock_httpx_get.return_value = predict_response

            response = client.get("/predictions/week/2024/1")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert data["succeeded"] == 1
