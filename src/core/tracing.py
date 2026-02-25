"""Request tracing middleware — generates and forwards X-Request-ID."""

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"

# Context variable for accessing request ID anywhere in the call stack
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique request ID to every request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Use client-provided ID or generate a new one
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Store in context var for downstream access
        token = request_id_var.set(request_id)

        try:
            response = await call_next(request)
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            request_id_var.reset(token)
