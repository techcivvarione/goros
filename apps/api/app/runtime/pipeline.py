"""Pipeline contracts for enriching runtime execution."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.runtime.context import RuntimeContext
from app.runtime.executor import RuntimeResult
from app.runtime.planner import RuntimePlan


class RuntimePipeline(ABC):
    """Boundary for runtime middleware that prepares or decorates execution."""

    @abstractmethod
    def process(self, plan: RuntimePlan, context: RuntimeContext) -> RuntimeResult:
        """Process a plan and return a runtime result."""
