"""API key authentication middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from src.core.config import settings

# Paths that don't require authentication
PUBLIC_PATHS = {"/", "/openapi.json", "/docs", "/redoc"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validate API key from X-API-Key header."""

    async def dispatch(self, request: Request, call_next):
        # Skip auth for public endpoints and OPTIONS preflight
        if request.url.path in PUBLIC_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        # Get valid API keys from config
        valid_keys = {k.strip() for k in settings.API_KEYS.split(",") if k.strip()}

        # If no keys configured, skip auth (development mode)
        if not valid_keys:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Missing API key. Include X-API-Key header.",
                    }
                },
            )

        if api_key not in valid_keys:
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Invalid API key.",
                    }
                },
            )

        return await call_next(request)
