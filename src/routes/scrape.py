from fastapi import APIRouter

router = APIRouter()

# TODO: Wire these to beat-books-data service
# Option A (now): pip install -e ../beat-books-data and import directly
# Option B (later): HTTP calls to beat-books-data at localhost:8001


@router.get("/{team}/{year}")
def scrape_team(team: str, year: int):
    """Trigger scraping for a single team/year. Delegates to beat-books-data."""
    # TODO: Call beat-books-data scrape service
    return {"message": f"Scrape {team}/{year} — not yet wired to beat-books-data"}


@router.get("/{year}")
def scrape_year(year: int):
    """Trigger scraping for all teams in a year. Delegates to beat-books-data."""
    # TODO: Call beat-books-data scrape service
    return {"message": f"Scrape all teams for {year} — not yet wired to beat-books-data"}


@router.post("/excel")
def scrape_excel():
    """Trigger batch scraping from Excel file. Delegates to beat-books-data."""
    # TODO: Call beat-books-data excel scraper service
    return {"message": "Excel scrape — not yet wired to beat-books-data"}
