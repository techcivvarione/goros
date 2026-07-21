"""API routes for system-level operational endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.core.dependencies import ApplicationContainer, get_container
from app.modules.system.api.schemas import (
    DependenciesResponse,
    LivenessResponse,
    ReadinessResponse,
)
from app.modules.system.application.system_service import SystemService

router = APIRouter(prefix="", tags=["System"])


def get_system_service(
    container: Annotated[ApplicationContainer, Depends(get_container)],
) -> SystemService:
    """Build the system service for operational endpoints."""

    return SystemService(settings=container.settings, database=container.database)


@router.get(
    "/health/live",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Return liveness status",
)
def get_liveness(
    service: Annotated[SystemService, Depends(get_system_service)],
) -> LivenessResponse:
    """Expose a lightweight liveness probe for orchestration."""

    return service.get_liveness()


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Return readiness status",
)
def get_readiness(
    response: Response,
    service: Annotated[SystemService, Depends(get_system_service)],
) -> ReadinessResponse:
    """Expose a readiness probe that validates critical dependencies."""

    readiness = service.get_readiness()
    if readiness.status != "UP":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return readiness


@router.get(
    "/health/dependencies",
    response_model=DependenciesResponse,
    status_code=status.HTTP_200_OK,
    summary="Return dependency status",
)
def get_dependencies(
    response: Response,
    service: Annotated[SystemService, Depends(get_system_service)],
) -> DependenciesResponse:
    """Expose dependency-level operational diagnostics."""

    dependencies = service.get_dependencies()
    if dependencies.status != "UP":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return dependencies
