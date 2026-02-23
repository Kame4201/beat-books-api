from fastapi import FastAPI
from src.routes import health, scrape, stats, predictions
from src.core.logging import RequestLoggingMiddleware, setup_logging

app = FastAPI(
    title="BeatTheBooks API",
    description="NFL game prediction platform — API gateway",
    version="1.0.0",
)

# Configure structured logging
setup_logging()

# Middleware
app.add_middleware(RequestLoggingMiddleware)

# Register route modules
app.include_router(health.router, tags=["Health"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scraping"])
app.include_router(stats.router, tags=["Statistics"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
