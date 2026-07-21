"""Infrastructure-level base class shared by all LLM provider adapters."""

from __future__ import annotations

from app.core.config import Settings
from app.modules.llm.domain.contracts import BaseProvider


class ProviderBase(BaseProvider):
    """Common infrastructure wiring shared by concrete provider adapters.

    Concrete providers (Ollama, OpenAI, Anthropic, Gemini) extend this class
    and implement the abstract methods declared on :class:`BaseProvider`.
    This class only supplies the shared constructor; it adds no
    provider-specific behavior.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the provider adapter with application settings."""

        self._settings = settings
