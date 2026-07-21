"""Top-level runtime orchestration contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.runtime.context import RuntimeContext
from app.runtime.executor import RuntimeResult


class RuntimeOrchestrator(ABC):
    """Boundary for the orchestration service coordinating runtime execution."""

    @abstractmethod
    def orchestrate(self, context: RuntimeContext) -> RuntimeResult:
        """Orchestrate a runtime request and return the normalized result."""
