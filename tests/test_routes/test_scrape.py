"""E2E tests for scrape routes."""
import pytest
from unittest.mock import AsyncMock, patch


class TestScrapeRoutes:
    """Tests for scraping endpoints."""

    @pytest.mark.asyncio
    async def test_scrape_team_success(self, client):
        """Test scraping a single team/year."""
        with patch(
            "src.routes.scrape.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "data": {"team": "KC", "year": 2024, "status": "completed"},
                "pagination": None,
            }

            response = client.get("/scrape/KC/2024")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["team"] == "KC"
            assert data["data"]["year"] == 2024
            assert data["data"]["status"] == "completed"
            mock_get.assert_called_once_with("/scrape/KC/2024")

    @pytest.mark.asyncio
    async def test_scrape_year_success(self, client):
        """Test scraping all teams for a year."""
        with patch(
            "src.routes.scrape.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "data": {
                    "year": 2024,
                    "teams_scraped": 32,
                    "status": "completed",
                },
                "pagination": None,
            }

            response = client.get("/scrape/2024")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["year"] == 2024
            assert data["data"]["teams_scraped"] == 32
            mock_get.assert_called_once_with("/scrape/2024")

    @pytest.mark.asyncio
    async def test_scrape_excel_success(self, client):
        """Test batch scraping from Excel file."""
        with patch(
            "src.routes.scrape.data_client.post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = {
                "data": {
                    "status": "completed",
                    "rows_processed": 100,
                },
                "pagination": None,
            }

            response = client.post("/scrape/excel")

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["status"] == "completed"
            assert data["data"]["rows_processed"] == 100
            mock_post.assert_called_once_with("/scrape/excel")

    @pytest.mark.asyncio
    async def test_scrape_service_unavailable(self, client):
        """Test handling data service unavailability."""
        from fastapi import HTTPException

        with patch(
            "src.routes.scrape.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = HTTPException(
                status_code=503,
                detail={
                    "error": {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": "Unable to connect to data service",
                    }
                },
            )

            response = client.get("/scrape/KC/2024")

            assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_scrape_not_found(self, client):
        """Test handling 404 from data service."""
        from fastapi import HTTPException

        with patch(
            "src.routes.scrape.data_client.get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Team not found",
                    }
                },
            )

            response = client.get("/scrape/INVALID/2024")

            assert response.status_code == 404
