"""Security contracts and request principal definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequestPrincipal:
    """Authenticated principal metadata attached to a request context."""

    subject: str
    organization_id: str | None
    scopes: tuple[str, ...]


class TokenVerifier(ABC):
    """Boundary for token verification implementations."""

    @abstractmethod
    def verify(self, token: str) -> RequestPrincipal:
        """Validate a token and return the resolved request principal."""


class AccessPolicy(ABC):
    """Boundary for authorization policy implementations."""

    @abstractmethod
    def assert_access(self, principal: RequestPrincipal, permission: str) -> None:
        """Raise an exception if the principal lacks the requested permission."""
