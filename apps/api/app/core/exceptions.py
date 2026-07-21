"""Application exception types and FastAPI exception handler registration."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, cast

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.shared.responses import ErrorResponse, error_response

logger = get_logger(__name__)
ExceptionHandler = Callable[[Request, Exception], Awaitable[JSONResponse]]


class GOROSException(Exception):
    """Base class for application-specific exceptions."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "internal_server_error"

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception with a message and optional details."""

        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_response(self) -> ErrorResponse:
        """Convert the exception into the standard API error response."""

        return error_response(
            code=self.error_code,
            message=self.message,
            details=self.details,
        )


class ValidationException(GOROSException):
    """Raised when a request fails validation."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "validation_error"


class AuthenticationException(GOROSException):
    """Raised when authentication fails."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "authentication_error"


class AuthorizationException(GOROSException):
    """Raised when access is denied."""

    status_code = status.HTTP_403_FORBIDDEN
    error_code = "authorization_error"


class NotFoundException(GOROSException):
    """Raised when a resource cannot be found."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class ConflictException(GOROSException):
    """Raised when a request conflicts with the current resource state."""

    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"


class InternalServerException(GOROSException):
    """Raised when an unexpected server-side failure occurs."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "internal_server_error"


def build_error_response(status_code: int, payload: ErrorResponse) -> JSONResponse:
    """Build a JSON response from a standard error payload."""

    return JSONResponse(status_code=status_code, content=payload.model_dump())


def log_exception_response(
    *,
    event: str,
    message: str,
    status_code: int,
    details: dict[str, Any],
    exc_info: bool = False,
) -> None:
    """Log exception responses using a consistent structured payload."""

    log_method = logger.exception if exc_info else logger.warning
    log_method(
        event,
        error_message=message,
        status_code=status_code,
        details=details,
    )


async def handle_goros_exception(_: Request, exc: GOROSException) -> JSONResponse:
    """Return a stable JSON error payload for known application exceptions."""

    log_exception_response(
        event="goros_exception",
        message=exc.message,
        status_code=exc.status_code,
        details={"error_code": exc.error_code, **exc.details},
    )
    return build_error_response(exc.status_code, exc.to_response())


async def handle_request_validation_error(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Translate FastAPI validation errors into the standard error response."""

    errors = exc.errors()
    log_exception_response(
        event="request_validation_error",
        message="Request validation failed.",
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        details={"errors": errors},
    )
    payload = error_response(
        code=ValidationException.error_code,
        message="Request validation failed.",
        details={"errors": errors},
    )
    return build_error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, payload)


async def handle_http_exception(
    _: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Translate Starlette HTTP exceptions into the standard error response."""

    detail = str(exc.detail)
    log_exception_response(
        event="http_exception",
        message=detail,
        status_code=exc.status_code,
        details={},
    )
    payload = error_response(
        code="http_error",
        message=detail,
        details={},
    )
    return build_error_response(exc.status_code, payload)


async def handle_unexpected_exception(_: Request, exc: Exception) -> JSONResponse:
    """Translate unexpected exceptions into the standard error response."""

    log_exception_response(
        event="unhandled_exception",
        message="An unexpected internal server error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"exception_type": exc.__class__.__name__},
        exc_info=True,
    )
    payload = error_response(
        code=InternalServerException.error_code,
        message="An unexpected internal server error occurred.",
        details={"exception_type": exc.__class__.__name__},
    )
    return build_error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, payload)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach application exception handlers to the FastAPI app."""

    app.add_exception_handler(
        GOROSException,
        cast(ExceptionHandler, handle_goros_exception),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, handle_request_validation_error),
    )
    app.add_exception_handler(
        StarletteHTTPException,
        cast(ExceptionHandler, handle_http_exception),
    )
    app.add_exception_handler(Exception, handle_unexpected_exception)
