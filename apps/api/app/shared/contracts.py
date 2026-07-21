"""Shared repository and unit-of-work contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Generic, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Base repository contract implemented by infrastructure adapters."""

    @abstractmethod
    def list(self) -> Iterable[T]:
        """Return an iterable view of aggregate roots managed by the repository."""


class UnitOfWork(ABC):
    """Boundary for transactional consistency across repositories."""

    @abstractmethod
    def commit(self) -> None:
        """Persist the current unit of work."""

    @abstractmethod
    def rollback(self) -> None:
        """Revert pending changes in the current unit of work."""
