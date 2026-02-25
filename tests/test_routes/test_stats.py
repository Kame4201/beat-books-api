"""E2E tests for stats routes."""

import pytest
from unittest.mock import AsyncMock, patch


class TestStatsRoutes:
    """Tests for statistics endpoints."""

    @pytest.mark.asyncio
    async def test_get_team_stats_success(self, client):
        """Test getting team stats with valid parameters."""
        with patch(
            "src.routes.stats.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "data": {"team": "KC", "season": 2024, "wins": 14, "losses": 3},
                "pagination": None,
            }

            response = client.get("/teams/KC/stats?season=2024")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["team"] == "KC"
            assert data["data"]["season"] == 2024
            mock_get.assert_called_once_with("/stats/teams/KC", params={"season": 2024})

    @pytest.mark.asyncio
    async def test_get_team_stats_invalid_season(self, client):
        """Test getting team stats with invalid season."""
        response = client.get("/teams/KC/stats?season=1800")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_players_success(self, client):
        """Test getting players with filtering."""
        with patch(
            "src.routes.stats.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "data": [
                    {"name": "Patrick Mahomes", "position": "QB", "team": "KC"},
                    {"name": "Josh Allen", "position": "QB", "team": "BUF"},
                ],
                "pagination": {"page": 1, "limit": 50, "total": 2, "total_pages": 1},
            }

            response = client.get("/players?season=2024&position=QB&page=1&limit=50")

            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 2
            assert data["pagination"]["total"] == 2
            mock_get.assert_called_once_with(
                "/stats/players",
                params={"season": 2024, "page": 1, "limit": 50, "position": "QB"},
            )

    @pytest.mark.asyncio
    async def test_get_players_invalid_position(self, client):
        """Test getting players with invalid position."""
        response = client.get("/players?season=2024&position=INVALID")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_players_invalid_pagination(self, client):
        """Test getting players with invalid pagination."""
        response = client.get("/players?season=2024&page=0")
        assert response.status_code == 422

        response = client.get("/players?season=2024&limit=300")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_games_success(self, client):
        """Test getting games."""
        with patch(
            "src.routes.stats.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "data": [
                    {"home_team": "KC", "away_team": "BUF", "week": 1, "season": 2024},
                ],
                "pagination": None,
            }

            response = client.get("/games?season=2024&week=1")

            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 1
            mock_get.assert_called_once_with(
                "/stats/games", params={"season": 2024, "week": 1}
            )

    @pytest.mark.asyncio
    async def test_get_games_without_week(self, client):
        """Test getting all games without week filter."""
        with patch(
            "src.routes.stats.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"data": [], "pagination": None}

            response = client.get("/games?season=2024")

            assert response.status_code == 200
            mock_get.assert_called_once_with("/stats/games", params={"season": 2024})

    @pytest.mark.asyncio
    async def test_get_games_invalid_week(self, client):
        """Test getting games with invalid week."""
        response = client.get("/games?season=2024&week=30")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_standings_success(self, client):
        """Test getting standings."""
        with patch(
            "src.routes.stats.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "data": [
                    {"team": "KC", "wins": 14, "losses": 3, "division": "AFC West"},
                    {"team": "BUF", "wins": 13, "losses": 4, "division": "AFC East"},
                ],
                "pagination": None,
            }

            response = client.get("/standings?season=2024")

            assert response.status_code == 200
            data = response.json()
            assert len(data["data"]) == 2
            mock_get.assert_called_once_with(
                "/stats/standings", params={"season": 2024}
            )

    @pytest.mark.asyncio
    async def test_empty_results(self, client):
        """Test handling empty results."""
        with patch(
            "src.routes.stats.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {"data": [], "pagination": None}

            response = client.get("/players?season=2024")

            assert response.status_code == 200
            data = response.json()
            assert data["data"] == []
