"""API router definition for the AI module."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.config import Settings
from app.core.dependencies import get_app_settings
from app.modules.ai.api.schemas import (
    ChatRequestSchema,
    ChatResponseData,
    ChatUsageSchema,
)
from app.modules.ai.application.ai_service import AIService
from app.modules.llm.application.factory import ProviderFactory
from app.modules.llm.application.manager import LLMManager
from app.modules.llm.application.model_registry import (
    build_model_registry_from_settings,
)
from app.modules.llm.application.model_resolver import ModelResolver
from app.modules.llm.application.registry import ProviderRegistry
from app.modules.llm.domain.entities import Message
from app.modules.llm.domain.enums import MessageRole
from app.shared import SuccessResponse, success_response

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


def get_ai_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> AIService:
    """Build the AI service for application-facing AI operations.

    Assembles the LLM Gateway chain (ProviderFactory, ProviderRegistry,
    ModelRegistry/ModelResolver, LLMManager) from settings and wraps it in
    an AIService. This builds fresh provider and registry instances on
    each resolution; wiring a process-wide singleton through the
    application container is deferred until this service is attached to
    real request traffic.
    """

    factory = ProviderFactory(settings)
    provider_registry = ProviderRegistry()
    model_registry = build_model_registry_from_settings(settings)
    model_resolver = ModelResolver(model_registry)
    llm_manager = LLMManager(
        factory=factory,
        registry=provider_registry,
        model_resolver=model_resolver,
    )
    return AIService(llm_manager=llm_manager)


@router.post(
    "/chat",
    response_model=SuccessResponse[ChatResponseData],
    status_code=status.HTTP_200_OK,
    summary="Generate a chat completion",
)
async def post_chat(
    payload: ChatRequestSchema,
    service: Annotated[AIService, Depends(get_ai_service)],
) -> SuccessResponse[ChatResponseData]:
    """Generate a chat completion for the given model alias.

    Delegates to :meth:`AIService.chat`; any provider or resolution failure
    (for example, an unreachable Ollama server) propagates to the
    application's existing global exception handlers, which return the
    standard error response envelope.
    """

    chat_response = await service.chat(
        messages=(Message(role=MessageRole.USER, content=payload.message),),
        model_alias=payload.model_alias,
        temperature=payload.temperature,
        system_prompt=payload.system_prompt,
    )

    usage = (
        ChatUsageSchema(
            prompt_tokens=chat_response.usage.prompt_tokens,
            completion_tokens=chat_response.usage.completion_tokens,
            total_tokens=chat_response.usage.total_tokens,
        )
        if chat_response.usage is not None
        else None
    )
    data = ChatResponseData(
        response=chat_response.message.content,
        provider=chat_response.provider,
        model=chat_response.model,
        usage=usage,
        finish_reason=chat_response.finish_reason,
    )
    return success_response(
        message="Chat completion generated successfully.",
        data=data,
    )
