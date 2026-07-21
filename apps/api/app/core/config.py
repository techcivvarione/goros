"""Application configuration for the GOROS API service."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import (
    AliasChoices,
    AnyHttpUrl,
    Field,
    SecretStr,
    computed_field,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["development", "staging", "production", "test"]


class Settings(BaseSettings):
    """Strongly typed application settings loaded from environment variables."""

    app_name: str = Field(default="GOROS", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: AppEnvironment = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")

    app_description: str = Field(
        default="Enterprise AI Operating System backend foundation for GOROS.",
        alias="APP_DESCRIPTION",
    )
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/goros",
        validation_alias=AliasChoices("DATABASE_URL", "POSTGRES_DSN"),
    )
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    supabase_url: AnyHttpUrl | None = Field(default=None, alias="SUPABASE_URL")
    supabase_key: SecretStr | None = Field(default=None, alias="SUPABASE_KEY")

    openai_url: AnyHttpUrl | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_URL", "OPENAI_BASE_URL"),
    )
    anthropic_url: AnyHttpUrl | None = Field(
        default=None,
        validation_alias=AliasChoices("ANTHROPIC_URL", "ANTHROPIC_BASE_URL"),
    )
    gemini_url: AnyHttpUrl | None = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI_URL", "GEMINI_BASE_URL"),
    )
    qdrant_url: AnyHttpUrl | None = Field(default=None, alias="QDRANT_URL")
    ollama_url: AnyHttpUrl | None = Field(default=None, alias="OLLAMA_URL")

    langfuse_host: AnyHttpUrl | None = Field(
        default=None,
        validation_alias=AliasChoices("LANGFUSE_HOST", "LANGFUSE_BASE_URL"),
    )
    langfuse_public_key: SecretStr | None = Field(
        default=None,
        alias="LANGFUSE_PUBLIC_KEY",
    )
    langfuse_secret_key: SecretStr | None = Field(
        default=None,
        alias="LANGFUSE_SECRET_KEY",
    )

    jwt_secret: SecretStr | None = Field(default=None, alias="JWT_SECRET")
    encryption_key: SecretStr | None = Field(default=None, alias="ENCRYPTION_KEY")

    redis_url: str | None = Field(default=None, alias="REDIS_URL")

    # Model alias bindings for the LLM Gateway's model registry. Each logical
    # alias (e.g. CHAT_FAST) maps to a provider name and a model name. Kept
    # as plain strings here (rather than the LLM module's ProviderType enum)
    # so this core configuration module has no dependency on a feature
    # module; the LLM module parses and validates these values itself.
    model_alias_chat_fast_provider: str = Field(
        default="ollama",
        alias="MODEL_ALIAS_CHAT_FAST_PROVIDER",
    )
    model_alias_chat_fast_model: str = Field(
        default="qwen3:8b",
        alias="MODEL_ALIAS_CHAT_FAST_MODEL",
    )
    model_alias_chat_premium_provider: str = Field(
        default="openai",
        alias="MODEL_ALIAS_CHAT_PREMIUM_PROVIDER",
    )
    model_alias_chat_premium_model: str = Field(
        default="gpt-5.5",
        alias="MODEL_ALIAS_CHAT_PREMIUM_MODEL",
    )
    model_alias_reasoning_provider: str = Field(
        default="anthropic",
        alias="MODEL_ALIAS_REASONING_PROVIDER",
    )
    model_alias_reasoning_model: str = Field(
        default="claude-opus",
        alias="MODEL_ALIAS_REASONING_MODEL",
    )
    model_alias_vision_provider: str = Field(
        default="ollama",
        alias="MODEL_ALIAS_VISION_PROVIDER",
    )
    model_alias_vision_model: str = Field(
        default="llama3.2-vision",
        alias="MODEL_ALIAS_VISION_MODEL",
    )
    model_alias_embeddings_provider: str = Field(
        default="ollama",
        alias="MODEL_ALIAS_EMBEDDINGS_PROVIDER",
    )
    model_alias_embeddings_model: str = Field(
        default="nomic-embed-text",
        alias="MODEL_ALIAS_EMBEDDINGS_MODEL",
    )

    openapi_contact_name: str = Field(
        default="GOROS Platform Team",
        alias="OPENAPI_CONTACT_NAME",
    )
    openapi_contact_email: str = Field(
        default="platform@goros.dev",
        alias="OPENAPI_CONTACT_EMAIL",
    )
    openapi_license_name: str = Field(
        default="Proprietary",
        alias="OPENAPI_LICENSE_NAME",
    )
    openapi_license_url: str = Field(
        default="https://goros.local/license",
        alias="OPENAPI_LICENSE_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("api_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        """Ensure the API prefix is always a normalized absolute path."""

        normalized = value.strip() or "/api/v1"
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        return normalized.rstrip("/") or "/"

    @computed_field
    def is_development(self) -> bool:
        """Return whether the application is running in a development environment."""

        return self.app_env == "development"

    @computed_field
    def is_production(self) -> bool:
        """Return whether the application is running in a production environment."""

        return self.app_env == "production"

    @property
    def environment(self) -> AppEnvironment:
        """Compatibility accessor for existing environment references."""

        return self.app_env

    @property
    def postgres_dsn(self) -> str:
        """Compatibility accessor for existing database DSN references."""

        return self.database_url

    @property
    def ollama_base_url(self) -> AnyHttpUrl | None:
        """Compatibility accessor for existing Ollama URL references."""

        return self.ollama_url

    @property
    def openai_base_url(self) -> AnyHttpUrl | None:
        """Compatibility accessor for existing OpenAI URL references."""

        return self.openai_url

    @property
    def anthropic_base_url(self) -> AnyHttpUrl | None:
        """Compatibility accessor for existing Anthropic URL references."""

        return self.anthropic_url

    @property
    def gemini_base_url(self) -> AnyHttpUrl | None:
        """Compatibility accessor for existing Gemini URL references."""

        return self.gemini_url

    @property
    def langfuse_base_url(self) -> AnyHttpUrl | None:
        """Compatibility accessor for existing Langfuse URL references."""

        return self.langfuse_host


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""

    return Settings()


settings = get_settings()
