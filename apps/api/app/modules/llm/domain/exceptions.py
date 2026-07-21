"""Domain-level exceptions for the LLM Gateway."""

from __future__ import annotations

from app.modules.llm.domain.enums import ModelAlias, ProviderType


class LLMGatewayError(Exception):
    """Base class for all LLM Gateway domain errors."""


class ProviderNotRegisteredError(LLMGatewayError):
    """Raised when a requested provider type has no registered adapter."""

    def __init__(self, provider_type: ProviderType) -> None:
        """Initialize the error with the unresolved provider type."""

        self.provider_type = provider_type
        super().__init__(f"Provider '{provider_type.value}' is not registered.")


class ProviderRequestError(LLMGatewayError):
    """Raised when a provider adapter fails to complete a request.

    Infrastructure adapters catch provider-SDK-specific exceptions (network
    failures, HTTP errors, and so on) and re-raise them as this domain
    exception, so callers never need to depend on a specific SDK's error
    types.
    """

    def __init__(self, provider_type: ProviderType, reason: str) -> None:
        """Initialize the error with the provider type and failure reason."""

        self.provider_type = provider_type
        self.reason = reason
        super().__init__(f"Provider '{provider_type.value}' request failed: {reason}")


class ModelAliasNotConfiguredError(LLMGatewayError):
    """Raised when a requested model alias has no configured definition."""

    def __init__(self, alias: ModelAlias) -> None:
        """Initialize the error with the unconfigured alias."""

        self.alias = alias
        super().__init__(f"Model alias '{alias.value}' is not configured.")


class ModelResolverNotConfiguredError(LLMGatewayError):
    """Raised when a ModelAlias is used but the manager has no ModelResolver."""

    def __init__(self) -> None:
        """Initialize the error with a fixed explanatory message."""

        super().__init__(
            "A ModelAlias was provided but this LLMManager has no "
            "ModelResolver configured."
        )
