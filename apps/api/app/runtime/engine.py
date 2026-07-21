"""Runtime engine contracts that coordinate planning and execution."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.runtime.context import RuntimeContext
from app.runtime.executor import RuntimeResult


class RuntimeEngine(ABC):
    """Boundary for the runtime entrypoint used by orchestration layers."""

    @abstractmethod
    def run(self, context: RuntimeContext) -> RuntimeResult:
        """Execute the runtime lifecycle for the supplied context."""
