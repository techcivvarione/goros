"""Shared value objects used across layers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HealthStatus:
    """Represents the current health of a process or dependency."""

    status: str
    service: str
    version: str


@dataclass(frozen=True, slots=True)
class ModuleDescriptor:
    """Identifies a module boundary within the application."""

    name: str
    display_name: str
