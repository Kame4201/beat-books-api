from fastapi import FastAPI
from src.routes import health, scrape, stats, predictions

app = FastAPI(
    title="BeatTheBooks API",
    description="NFL game prediction platform — API gateway",
    version="1.0.0",
)

# Register route modules
app.include_router(health.router, tags=["Health"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scraping"])
app.include_router(stats.router, tags=["Statistics"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
