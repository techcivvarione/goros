"""HTTP middleware registration for request tracing and operational logging."""

from __future__ import annotations

import time
import uuid

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.logging import get_logger

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach request-scoped context for tracing and structured logging."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware with the ASGI app."""

        super().__init__(app)
        self.logger = get_logger(__name__)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Bind request context, emit request logs, and add the request ID header."""

        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        organization_id = request.headers.get("X-Organization-ID")
        user_id = request.headers.get("X-User-ID")
        module = self._resolve_module(request.url.path)
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            module=module,
            organization_id=organization_id,
            user_id=user_id,
        )

        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            structlog.contextvars.bind_contextvars(latency=latency_ms)
            self.logger.exception(
                "request_failed",
                method=request.method,
                path=request.url.path,
            )
            raise
        else:
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            request.state.latency = latency_ms
            structlog.contextvars.bind_contextvars(latency=latency_ms)

            self.logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            response.headers["X-Execution-Time-ms"] = str(latency_ms)
            return response
        finally:
            structlog.contextvars.clear_contextvars()

    @staticmethod
    def _resolve_module(path: str) -> str:
        """Infer the top-level module name from the request path."""

        parts = [part for part in path.split("/") if part]
        if not parts:
            return "root"
        if len(parts) >= 3 and parts[0] == "api":
            return parts[2]
        return parts[0]


def register_middleware(app: FastAPI) -> None:
    """Register all HTTP middleware for the FastAPI application."""

    app.add_middleware(RequestContextMiddleware)
