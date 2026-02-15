from fastapi import FastAPI
from src.services import scrape_service, team_offense_service, excel_scraper_service

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}



@app.get("/scrape/{team}/{year}")
async def scrape_data(team: str, year: int):
    """
    Docstring for scrape_data function. scrapes data from team of choice.
    Args:
        team (str): The team to scrape data for.
        year (int): The year to scrape data for.
    Returns:
        dict: A dictionary containing the scraping result.
    """

    data = await scrape_service.scrape_and_store(team, year)
    return data



@app.get("/scrape/{year}")
async def scrape_team_offense(year: int):


    data = await team_offense_service.scrape_and_store_team_offense(year)
    return data


@app.post("/scrape/excel")
async def scrape_from_excel_file(excel_path: str):
    """
    Scrape Pro-Football-Reference URLs from an Excel file and store results in database.

    The Excel file should contain:
    - url (required): The Pro-Football-Reference URL to scrape
    - season (optional): Season year
    - entity_type (optional): Type of entity being scraped
    - table_type (optional): Type of table being scraped

    Args:
        excel_path (str): Path to the Excel file containing URLs to scrape

    Returns:
        dict: Summary of scraping results including:
            - urls_processed: Number of URLs attempted
            - urls_success: Number of URLs successfully scraped
            - urls_failed: Number of URLs that failed
            - tables_extracted: Total number of tables extracted
            - rows_inserted: Total number of rows inserted
            - errors: List of error messages (if any)

    Example:
        POST /scrape/excel?excel_path=/path/to/urls.xlsx
    """
    results = await excel_scraper_service.scrape_from_excel(excel_path)
    return results