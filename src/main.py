from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from src.core.rate_limit import limiter
from src.routes import health, scrape, stats, predictions
from src.core.config import settings
from src.core.auth import APIKeyMiddleware

app = FastAPI(
    title="BeatTheBooks API",
    description="NFL game prediction platform — API gateway",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Return 429 with Retry-After header when rate limit is exceeded."""
    retry_after = exc.detail.split("per")[-1].strip() if exc.detail else "60"
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "RATE_LIMITED",
                "message": f"Rate limit exceeded: {exc.detail}",
            }
        },
        headers={"Retry-After": retry_after},
    )

# Authentication middleware
app.add_middleware(APIKeyMiddleware)

# Register route modules
app.include_router(health.router, tags=["Health"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scraping"])
app.include_router(stats.router, tags=["Statistics"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
