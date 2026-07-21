"""Execution contracts for runtime plans."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.runtime.context import RuntimeContext
from app.runtime.planner import RuntimePlan


@dataclass(slots=True)
class RuntimeResult:
    """Normalized runtime execution result returned by the executor."""

    status: str
    payload: dict[str, object] = field(default_factory=dict)


class RuntimeExecutor(ABC):
    """Boundary for executing prepared runtime plans."""

    @abstractmethod
    def execute(self, plan: RuntimePlan, context: RuntimeContext) -> RuntimeResult:
        """Execute the provided runtime plan within the supplied context."""
