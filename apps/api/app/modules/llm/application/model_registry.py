"""Model registry for the LLM Gateway.

Implements the Registry pattern: an in-memory lookup of concrete
provider/model bindings keyed by logical :class:`ModelAlias`. Applications
request a role such as ``ModelAlias.CHAT_FAST`` instead of naming a specific
provider and model, so the concrete binding can change (or be reconfigured
per environment) without any application code changes.
"""

from __future__ import annotations

from app.core.config import Settings
from app.modules.llm.domain.entities import ModelDefinition
from app.modules.llm.domain.enums import ModelAlias, ModelCapability, ProviderType
from app.modules.llm.domain.exceptions import ModelAliasNotConfiguredError

# Default capability tags per alias, derived from what each alias means.
# These describe the expectation for the role, not a specific model's
# verified feature set.
_DEFAULT_CAPABILITIES: dict[ModelAlias, tuple[ModelCapability, ...]] = {
    ModelAlias.CHAT_FAST: (ModelCapability.CHAT, ModelCapability.STREAMING),
    ModelAlias.CHAT_PREMIUM: (ModelCapability.CHAT, ModelCapability.STREAMING),
    ModelAlias.REASONING: (ModelCapability.CHAT, ModelCapability.REASONING),
    ModelAlias.VISION: (ModelCapability.CHAT, ModelCapability.VISION),
    ModelAlias.EMBEDDINGS: (ModelCapability.EMBEDDINGS,),
}


class ModelRegistry:
    """In-memory registry mapping model aliases to concrete model definitions."""

    def __init__(
        self,
        definitions: dict[ModelAlias, ModelDefinition] | None = None,
    ) -> None:
        """Initialize the registry, optionally pre-populated with definitions."""

        self._definitions: dict[ModelAlias, ModelDefinition] = dict(definitions or {})

    def register(self, definition: ModelDefinition) -> None:
        """Register (or replace) the model definition for its alias."""

        self._definitions[definition.alias] = definition

    def get(self, alias: ModelAlias) -> ModelDefinition:
        """Return the model definition registered for the given alias."""

        try:
            return self._definitions[alias]
        except KeyError as exc:
            raise ModelAliasNotConfiguredError(alias) from exc

    def is_registered(self, alias: ModelAlias) -> bool:
        """Return whether a definition has been registered for the given alias."""

        return alias in self._definitions

    def list_registered(self) -> tuple[ModelAlias, ...]:
        """Return the aliases currently registered."""

        return tuple(self._definitions.keys())


def build_model_registry_from_settings(settings: Settings) -> ModelRegistry:
    """Build a ModelRegistry pre-populated from application configuration.

    Reads the provider/model pair configured for each :class:`ModelAlias`
    from :class:`Settings` and registers a :class:`ModelDefinition` for it.
    An invalid provider name in configuration raises ``ValueError`` via
    :class:`ProviderType`'s own value validation.
    """

    pairs: dict[ModelAlias, tuple[str, str]] = {
        ModelAlias.CHAT_FAST: (
            settings.model_alias_chat_fast_provider,
            settings.model_alias_chat_fast_model,
        ),
        ModelAlias.CHAT_PREMIUM: (
            settings.model_alias_chat_premium_provider,
            settings.model_alias_chat_premium_model,
        ),
        ModelAlias.REASONING: (
            settings.model_alias_reasoning_provider,
            settings.model_alias_reasoning_model,
        ),
        ModelAlias.VISION: (
            settings.model_alias_vision_provider,
            settings.model_alias_vision_model,
        ),
        ModelAlias.EMBEDDINGS: (
            settings.model_alias_embeddings_provider,
            settings.model_alias_embeddings_model,
        ),
    }

    registry = ModelRegistry()
    for alias, (provider_name, model_name) in pairs.items():
        registry.register(
            ModelDefinition(
                alias=alias,
                provider=ProviderType(provider_name),
                model=model_name,
                capabilities=_DEFAULT_CAPABILITIES[alias],
            )
        )
    return registry
