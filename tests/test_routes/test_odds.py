"""Tests for odds endpoints."""

from unittest.mock import AsyncMock, patch

SAMPLE_ODDS_LINE = {
    "game_id": "2024-W1-KC-DET",
    "book": "draftkings",
    "home_team": "chiefs",
    "away_team": "lions",
    "spread": -3.5,
    "total": 48.5,
    "home_moneyline": -175,
    "away_moneyline": 150,
    "timestamp": "2024-09-05T18:00:00Z",
}


class TestLiveOdds:
    """Tests for GET /odds/live."""

    def test_get_live_odds_success(self, client):
        with patch(
            "src.routes.odds.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"data": [SAMPLE_ODDS_LINE]}
            response = client.get("/odds/live")
            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 1
            assert data["data"][0]["game_id"] == "2024-W1-KC-DET"

    def test_get_live_odds_with_sport_param(self, client):
        with patch(
            "src.routes.odds.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"data": []}
            response = client.get("/odds/live?sport=nfl")
            assert response.status_code == 200
            mock_get.assert_called_once_with("/odds/live", params={"sport": "nfl"})

    def test_get_live_odds_empty(self, client):
        with patch(
            "src.routes.odds.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"data": []}
            response = client.get("/odds/live")
            assert response.status_code == 200
            assert response.json()["data"] == []


class TestOddsHistory:
    """Tests for GET /odds/history/{game_id}."""

    def test_get_odds_history_success(self, client):
        with patch(
            "src.routes.odds.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "game_id": "2024-W1-KC-DET",
                "history": [SAMPLE_ODDS_LINE],
            }
            response = client.get("/odds/history/2024-W1-KC-DET")
            assert response.status_code == 200
            data = response.json()
            assert data["game_id"] == "2024-W1-KC-DET"
            assert len(data["history"]) == 1

    def test_get_odds_history_delegates_to_data_service(self, client):
        with patch(
            "src.routes.odds.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "game_id": "game-123",
                "history": [],
            }
            client.get("/odds/history/game-123")
            mock_get.assert_called_once_with("/odds/history/game-123")


class TestBestOdds:
    """Tests for GET /odds/best."""

    def test_get_best_odds_success(self, client):
        with patch(
            "src.routes.odds.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"data": [SAMPLE_ODDS_LINE]}
            response = client.get("/odds/best")
            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 1

    def test_get_best_odds_with_sport_param(self, client):
        with patch(
            "src.routes.odds.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"data": []}
            response = client.get("/odds/best?sport=nfl")
            assert response.status_code == 200
            mock_get.assert_called_once_with("/odds/best", params={"sport": "nfl"})


class TestOddsOpenAPI:
    """Tests that odds endpoints appear in OpenAPI schema."""

    def test_odds_routes_in_openapi(self, client):
        schema = client.get("/openapi.json").json()
        paths = set(schema["paths"].keys())
        assert "/odds/live" in paths
        assert "/odds/history/{game_id}" in paths
        assert "/odds/best" in paths
