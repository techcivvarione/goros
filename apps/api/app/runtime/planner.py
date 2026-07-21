"""Planning contracts for runtime execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.runtime.context import RuntimeContext


@dataclass(slots=True)
class RuntimePlan:
    """A normalized runtime execution plan prepared before orchestration."""

    operation: str
    module: str
    parameters: dict[str, str] = field(default_factory=dict)


class RuntimePlanner(ABC):
    """Boundary for converting requests into runtime execution plans."""

    @abstractmethod
    def build_plan(self, context: RuntimeContext) -> RuntimePlan:
        """Create a runtime plan from the incoming request context."""
