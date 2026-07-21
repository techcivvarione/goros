"""Shared contracts and cross-cutting types used across modules."""

from app.shared.contracts import Repository, UnitOfWork
from app.shared.responses import (
    ErrorDetail,
    ErrorResponse,
    SuccessResponse,
    error_response,
    success_response,
)
from app.shared.types import HealthStatus, ModuleDescriptor

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "HealthStatus",
    "ModuleDescriptor",
    "Repository",
    "SuccessResponse",
    "UnitOfWork",
    "error_response",
    "success_response",
]
