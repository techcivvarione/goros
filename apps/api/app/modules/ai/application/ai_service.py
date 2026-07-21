"""Application service exposing AI operations as GOROS's single AI entry point.

AIService is the only supported entry point for application code that needs
AI capabilities. Application code must never construct a ChatRequest or call
LLMManager directly -- it calls AIService, which owns that translation
internally.
"""

from __future__ import annotations

from app.modules.llm.application.manager import LLMManager
from app.modules.llm.domain.entities import ChatRequest, ChatResponse, Message
from app.modules.llm.domain.enums import ModelAlias, ProviderType


class AIService:
    """Single public entry point for AI operations across GOROS.

    Only :meth:`chat` is implemented this sprint. The remaining methods are
    declared to establish the service's intended surface and raise
    ``NotImplementedError`` until their respective sprints implement them;
    none have an agreed parameter or return shape yet, so none are
    fabricated here.
    """

    def __init__(self, llm_manager: LLMManager) -> None:
        """Initialize the service with the injected LLM manager."""

        self._llm_manager = llm_manager

    async def chat(
        self,
        messages: tuple[Message, ...],
        model_alias: ModelAlias,
        *,
        temperature: float | None = None,
        system_prompt: str | None = None,
    ) -> ChatResponse:
        """Generate a chat completion for the given model alias.

        Callers supply only messages and a logical :class:`ModelAlias`; the
        concrete :class:`ChatRequest` is built internally and its
        provider/model are resolved through the injected
        :class:`LLMManager`, so application code never constructs a
        ChatRequest itself and never needs to know which provider backs a
        given alias.
        """

        request = ChatRequest(
            # provider/model are placeholders: LLMManager.chat() resolves
            # and overrides both from `model_alias` before delegating to a
            # provider, since `alias` is always supplied below.
            provider=ProviderType.OLLAMA,
            model="",
            messages=messages,
            temperature=temperature,
            system_prompt=system_prompt,
        )
        return await self._llm_manager.chat(request, alias=model_alias)

    async def summarize(self) -> None:
        """Summarize content. Not yet implemented."""

        raise NotImplementedError("AIService.summarize is not yet implemented.")

    async def classify(self) -> None:
        """Classify content. Not yet implemented."""

        raise NotImplementedError("AIService.classify is not yet implemented.")

    async def extract(self) -> None:
        """Extract structured data from content. Not yet implemented."""

        raise NotImplementedError("AIService.extract is not yet implemented.")

    async def rewrite(self) -> None:
        """Rewrite content. Not yet implemented."""

        raise NotImplementedError("AIService.rewrite is not yet implemented.")

    async def translate(self) -> None:
        """Translate content. Not yet implemented."""

        raise NotImplementedError("AIService.translate is not yet implemented.")

    async def generate_title(self) -> None:
        """Generate a title for content. Not yet implemented."""

        raise NotImplementedError("AIService.generate_title is not yet implemented.")

    async def generate_tags(self) -> None:
        """Generate tags for content. Not yet implemented."""

        raise NotImplementedError("AIService.generate_tags is not yet implemented.")
