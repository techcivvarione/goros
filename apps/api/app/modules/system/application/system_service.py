"""Application services for system-level operational endpoints."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.core.database import DatabaseManager
from app.core.logging import get_logger
from app.modules.system.api.schemas import (
    DependenciesResponse,
    DependencyConfigurationStatus,
    DependencyStatus,
    HealthProbeStatus,
    LivenessResponse,
    ReadinessResponse,
)

logger = get_logger(__name__)


class SystemService:
    """Encapsulates system health and dependency inspection logic."""

    def __init__(self, settings: Settings, database: DatabaseManager) -> None:
        """Initialize the service with infrastructure dependencies."""

        self.settings = settings
        self.database = database

    def get_liveness(self) -> LivenessResponse:
        """Return the liveness probe response."""

        return LivenessResponse(status="UP")

    def get_readiness(self) -> ReadinessResponse:
        """Return application readiness based on critical dependencies."""

        database_status: HealthProbeStatus = (
            "UP" if self._is_database_ready() else "DOWN"
        )
        overall_status: HealthProbeStatus = "UP" if database_status == "UP" else "DOWN"
        return ReadinessResponse(
            status=overall_status,
            checks={"database": database_status},
        )

    def get_dependencies(self) -> DependenciesResponse:
        """Return dependency status details for operational diagnostics."""

        database_up = self._is_database_ready()
        config_up = self._is_configuration_ready()
        redis_state: DependencyConfigurationStatus = (
            "CONFIGURED" if self.settings.redis_url else "NOT_CONFIGURED"
        )
        qdrant_state: DependencyConfigurationStatus = (
            "CONFIGURED" if self.settings.qdrant_url else "NOT_CONFIGURED"
        )

        overall_status: HealthProbeStatus = (
            "UP" if database_up and config_up else "DOWN"
        )
        return DependenciesResponse(
            status=overall_status,
            checks={
                "database": DependencyStatus(
                    status="UP" if database_up else "DOWN",
                    details={"url": self._mask_database_url()},
                ),
                "configuration": DependencyStatus(
                    status="UP" if config_up else "DOWN",
                    details={
                        "app_env": self.settings.app_env,
                        "debug": str(self.settings.debug).lower(),
                    },
                ),
                "redis": DependencyStatus(
                    status=redis_state,
                    details={"placeholder": "Future readiness check not enabled."},
                ),
                "qdrant": DependencyStatus(
                    status=qdrant_state,
                    details={"placeholder": "Future readiness check not enabled."},
                ),
            },
        )

    def _is_database_ready(self) -> bool:
        """Return whether the primary database connection is healthy."""

        try:
            return self.database.healthcheck()
        except SQLAlchemyError:
            logger.warning("system_database_healthcheck_failed", module="system")
            return False

    def _is_configuration_ready(self) -> bool:
        """Return whether required platform configuration is present."""

        return bool(
            self.settings.app_name
            and self.settings.app_version
            and self.settings.database_url
        )

    def _mask_database_url(self) -> str:
        """Return a non-sensitive representation of the database DSN."""

        return self.settings.database_url.rsplit("@", maxsplit=1)[-1]
