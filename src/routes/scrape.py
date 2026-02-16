from fastapi import APIRouter
from src.core.client import data_client

router = APIRouter()


@router.get("/{team}/{year}")
async def scrape_team(team: str, year: int):
    """Trigger scraping for a single team/year. Delegates to beat-books-data."""
    result = await data_client.get(f"/scrape/{team}/{year}")
    return result


@router.get("/{year}")
async def scrape_year(year: int):
    """Trigger scraping for all teams in a year. Delegates to beat-books-data."""
    result = await data_client.get(f"/scrape/{year}")
    return result


@router.post("/excel")
async def scrape_excel():
    """Trigger batch scraping from Excel file. Delegates to beat-books-data."""
    result = await data_client.post("/scrape/excel")
    return result
