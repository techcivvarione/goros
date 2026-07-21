"""Standard API response contracts used across the application."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Standardized error payload."""

    code: str = Field(description="Stable machine-readable error code.")
    message: str = Field(description="Human-readable error description.")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional structured error context.",
    )


class SuccessResponse(BaseModel, Generic[T]):
    """Standardized success response payload."""

    success: bool = Field(default=True)
    message: str = Field(description="Human-readable success message.")
    data: T = Field(description="Success payload.")


class ErrorResponse(BaseModel):
    """Standardized error response payload."""

    success: bool = Field(default=False)
    error: ErrorDetail


def success_response(message: str, data: T) -> SuccessResponse[T]:
    """Build a success response payload."""

    return SuccessResponse(message=message, data=data)


def error_response(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> ErrorResponse:
    """Build an error response payload."""

    return ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details or {},
        )
    )
