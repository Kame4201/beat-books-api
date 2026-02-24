"""Structured JSON logging middleware for request/response tracking."""

import json
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from src.core.config import settings

logger = logging.getLogger("beat-books-api")


def setup_logging() -> None:
    """Configure structured JSON logging."""
    root_logger = logging.getLogger("beat-books-api")
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    root_logger.disabled = False

    if not any(getattr(h, "_beat_books_handler", False) for h in root_logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        handler._beat_books_handler = True  # type: ignore[attr-defined]
        root_logger.addHandler(handler)

    root_logger.propagate = False


class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)
        return json.dumps(log_entry)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status, and duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()

        response = await call_next(request)

        duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        extra = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else None,
        }

        # Keep middleware logs compatible with pytest's log capture (caplog),
        # which captures records via the root logger handler.
        logger.propagate = True

        logger.info(
            "%s %s %s %sms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={"extra_data": extra},
        )

        return response
