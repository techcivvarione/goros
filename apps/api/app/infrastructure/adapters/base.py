"""Base contracts shared by infrastructure adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AdapterConfiguration:
    """Normalized adapter configuration returned by infrastructure adapters."""

    name: str
    endpoint: str | None


class ConfigurableAdapter(ABC):
    """Base adapter contract exposing normalized configuration metadata."""

    @abstractmethod
    def configuration(self) -> AdapterConfiguration:
        """Return the normalized configuration for this adapter."""


def normalize_endpoint(endpoint: Any) -> str | None:
    """Convert configured endpoint values into optional string representations."""

    if endpoint is None:
        return None
    return str(endpoint)
