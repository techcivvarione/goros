"""Model resolver for the LLM Gateway.

Resolves a logical :class:`ModelAlias` into a concrete
:class:`ModelDefinition` (provider and model) by consulting the
:class:`ModelRegistry`, so callers never need to know which provider backs
a given alias.
"""

from __future__ import annotations

from app.modules.llm.application.model_registry import ModelRegistry
from app.modules.llm.domain.entities import ChatRequest, Message, ModelDefinition
from app.modules.llm.domain.enums import ModelAlias


class ModelResolver:
    """Resolves logical model aliases into concrete provider/model bindings."""

    def __init__(self, registry: ModelRegistry) -> None:
        """Initialize the resolver with a model registry."""

        self._registry = registry

    def resolve(self, alias: ModelAlias) -> ModelDefinition:
        """Return the concrete model definition bound to the given alias."""

        return self._registry.get(alias)


def build_chat_request_for_alias(
    resolver: ModelResolver,
    alias: ModelAlias,
    messages: tuple[Message, ...],
) -> ChatRequest:
    """Build a ChatRequest for a model alias without naming a provider.

    Resolves ``alias`` through ``resolver`` and uses the resolved
    provider/model to construct the request, so callers that only know the
    alias never need to reference a :class:`ProviderType` at all. Any other
    :class:`ChatRequest` field can be set afterwards with
    ``dataclasses.replace``.
    """

    definition = resolver.resolve(alias)
    return ChatRequest(
        provider=definition.provider,
        model=definition.model,
        messages=messages,
    )
