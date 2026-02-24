from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import health, scrape, stats, predictions
<<<<<<< feat/issue-17-logging
from src.core.logging import RequestLoggingMiddleware, setup_logging
=======
from src.core.config import settings
>>>>>>> dev

app = FastAPI(
    title="BeatTheBooks API",
    description="NFL game prediction platform — API gateway",
    version="1.0.0",
)

<<<<<<< feat/issue-17-logging
# Configure structured logging
setup_logging()

# Middleware
app.add_middleware(RequestLoggingMiddleware)
=======
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
>>>>>>> dev

# Register route modules
app.include_router(health.router, tags=["Health"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scraping"])
app.include_router(stats.router, tags=["Statistics"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
