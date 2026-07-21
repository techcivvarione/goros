"""Runtime request context definitions."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.security import RequestPrincipal


@dataclass(slots=True)
class RuntimeContext:
    """Immutable request-scoped context consumed by the runtime pipeline."""

    request_id: str
    principal: RequestPrincipal | None = None
    conversation_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
