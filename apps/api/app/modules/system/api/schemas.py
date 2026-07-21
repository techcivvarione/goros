"""Schemas for system-level operational endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

HealthProbeStatus = Literal["UP", "DOWN"]
DependencyConfigurationStatus = Literal["UP", "DOWN", "CONFIGURED", "NOT_CONFIGURED"]


class LivenessResponse(BaseModel):
    """Response payload for the liveness probe."""

    status: HealthProbeStatus = Field(default="UP", description="Liveness state.")


class ReadinessResponse(BaseModel):
    """Response payload for the readiness probe."""

    status: HealthProbeStatus = Field(
        description="Readiness state for the application.",
    )
    checks: dict[str, HealthProbeStatus] = Field(
        description="Dependency readiness results.",
    )


class DependencyStatus(BaseModel):
    """Operational status of a single dependency."""

    status: DependencyConfigurationStatus = Field(description="Dependency state.")
    details: dict[str, str] = Field(default_factory=dict)


class DependenciesResponse(BaseModel):
    """Response payload for dependency inspection."""

    status: HealthProbeStatus = Field(description="Overall dependency state.")
    checks: dict[str, DependencyStatus] = Field(description="Dependency details.")
