import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ModuleNotFoundError:
    Instrumentator = None
    logging.getLogger(__name__).info(
        "prometheus-fastapi-instrumentator not installed — metrics endpoint disabled"
    )
from src.core.rate_limit import limiter
from src.core.tracing import RequestTracingMiddleware
from src.core.logging import RequestLoggingMiddleware
from src.core.auth import APIKeyMiddleware
from src.core.config import settings
from src.routes import health, scrape, stats, predictions, odds

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

# Authentication middleware
app.add_middleware(APIKeyMiddleware)

# Request/response logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Request tracing middleware
app.add_middleware(RequestTracingMiddleware)

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


# Register route modules
app.include_router(health.router, tags=["Health"])
app.include_router(scrape.router, prefix="/scrape", tags=["Scraping"])
app.include_router(stats.router, tags=["Statistics"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(odds.router, prefix="/odds", tags=["Odds"])

# Prometheus metrics — exposes /metrics endpoint
if Instrumentator is not None:
    Instrumentator(
        excluded_handlers=["/metrics"],
    ).instrument(
        app
    ).expose(app, endpoint="/metrics", tags=["Monitoring"])
