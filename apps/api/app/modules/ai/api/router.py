"""API router definition for the AI module."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from app.core.config import Settings
from app.core.dependencies import get_app_settings
from app.core.logging import get_logger
from app.modules.ai.api.schemas import (
    ChatRequestSchema,
    ChatResponseData,
    ChatStreamRequestSchema,
    ChatUsageSchema,
)
from app.modules.ai.application.ai_service import AIService
from app.modules.conversations.api.router import (
    get_conversation_service,
    get_message_service,
)
from app.modules.conversations.application.conversation_service import (
    ConversationService,
)
from app.modules.conversations.application.message_service import MessageService
from app.modules.conversations.domain.entities import ConversationMessage
from app.modules.conversations.domain.enums import MessageStatus
from app.modules.llm.application.factory import ProviderFactory
from app.modules.llm.application.manager import LLMManager
from app.modules.llm.application.model_registry import (
    build_model_registry_from_settings,
)
from app.modules.llm.application.model_resolver import ModelResolver
from app.modules.llm.application.registry import ProviderRegistry
from app.modules.llm.domain.entities import Message
from app.modules.llm.domain.enums import MessageRole
from app.modules.llm.domain.exceptions import (
    ModelAliasNotConfiguredError,
    ModelResolverNotConfiguredError,
    ProviderNotRegisteredError,
    ProviderRequestError,
)
from app.shared import SuccessResponse, success_response

logger = get_logger(__name__)

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


def _build_context_messages(
    message_service: MessageService,
    conversation_id: UUID | None,
    new_user_content: str,
) -> tuple[Message, ...]:
    """Build the full message context sent to AIService for this turn.

    If ``conversation_id`` is given, every existing message already
    persisted for that conversation is loaded via
    :meth:`MessageService.list_by_conversation` -- ordered oldest first,
    exactly as stored, with no filtering, truncation, or summarization (per
    Sprint 7: "Use every message for now") -- and the new user message is
    appended after it, so the model sees the full conversation history.
    Token window management and summarization are explicitly deferred to a
    future Memory implementation.

    Must be called before the new user message is persisted, otherwise the
    freshly saved message would be loaded here *and* appended again below.

    If ``conversation_id`` is omitted, behavior is unchanged from Sprint 3:
    only the new message is sent, exactly as before.
    """

    new_message = Message(role=MessageRole.USER, content=new_user_content)
    if conversation_id is None:
        return (new_message,)

    history = message_service.list_by_conversation(conversation_id)
    context = tuple(
        Message(role=existing.role, content=existing.content) for existing in history
    )
    return (*context, new_message)


@router.post(
    "/chat",
    response_model=SuccessResponse[ChatResponseData],
    status_code=status.HTTP_200_OK,
    summary="Generate a chat completion",
)
async def post_chat(
    payload: ChatRequestSchema,
    service: Annotated[AIService, Depends(get_ai_service)],
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    message_service: Annotated[MessageService, Depends(get_message_service)],
) -> SuccessResponse[ChatResponseData]:
    """Generate a chat completion for the given model alias.

    If ``conversation_id`` is omitted, behavior is unchanged from Sprint 3:
    no validation, no persistence, no history, chat proceeds exactly as
    before.

    If supplied: the conversation must exist (and not be soft-deleted) --
    a missing conversation propagates through the existing Conversations
    exception mapping as a standard 404 error response -- then every
    message already in the conversation is loaded (oldest first, no
    filtering or truncation) and sent to the model ahead of the new user
    message, so the AI automatically has the conversation's context. The
    user's message is persisted, the chat completion is generated, and the
    assistant's reply is persisted before the response is returned. If the
    chat call itself fails (for example, an unreachable Ollama server), the
    user message remains persisted but no assistant message is written; the
    failure still propagates through the existing global exception handlers
    as a standard error response.

    Delegates to :meth:`AIService.chat`; any provider or resolution failure
    propagates to the application's existing global exception handlers.
    """

    if payload.conversation_id is not None:
        conversation_service.get(payload.conversation_id)

    # Must run before persisting the new user message below, or that
    # message would be loaded as history and then appended again.
    context_messages = _build_context_messages(
        message_service, payload.conversation_id, payload.message
    )

    if payload.conversation_id is not None:
        message_service.create(
            conversation_id=payload.conversation_id,
            role=MessageRole.USER,
            content=payload.message,
        )

    chat_response = await service.chat(
        messages=context_messages,
        model_alias=payload.model_alias,
        temperature=payload.temperature,
        system_prompt=payload.system_prompt,
    )

    if payload.conversation_id is not None:
        message_service.create(
            conversation_id=payload.conversation_id,
            role=MessageRole.ASSISTANT,
            content=chat_response.message.content,
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


_STREAM_ERROR_CODE_BY_EXCEPTION: dict[type[Exception], str] = {
    ProviderRequestError: "provider_unavailable",
    ProviderNotRegisteredError: "provider_not_registered",
    ModelAliasNotConfiguredError: "model_alias_not_configured",
    ModelResolverNotConfiguredError: "model_resolver_not_configured",
}


def _stream_error_payload(exc: Exception) -> tuple[str, str]:
    """Map a mid-stream failure to the same error code/message the JSON API uses.

    A streaming response has already sent a 200 status and started sending
    body bytes by the time generation can fail, so the failure cannot be
    reported through the application's global exception handlers (which work
    by choosing an HTTP status code before any response is sent). This
    mirrors the safety guarantees of ``app.core.exceptions`` for that one
    path instead: never surface provider SDK exception text or a stack trace
    in the event payload.
    """

    if isinstance(exc, ProviderRequestError):
        code = _STREAM_ERROR_CODE_BY_EXCEPTION[ProviderRequestError]
        message = f"The '{exc.provider_type.value}' provider is currently unavailable."
        return code, message
    if isinstance(exc, ProviderNotRegisteredError):
        code = _STREAM_ERROR_CODE_BY_EXCEPTION[ProviderNotRegisteredError]
        return code, f"Provider '{exc.provider_type.value}' is not registered."
    if isinstance(exc, ModelAliasNotConfiguredError):
        code = _STREAM_ERROR_CODE_BY_EXCEPTION[ModelAliasNotConfiguredError]
        return code, f"Model alias '{exc.alias.value}' is not configured."
    if isinstance(exc, ModelResolverNotConfiguredError):
        code = _STREAM_ERROR_CODE_BY_EXCEPTION[ModelResolverNotConfiguredError]
        return code, "No model resolver is configured for this request."
    return "internal_server_error", "An unexpected internal server error occurred."


def _sse_event(payload: dict[str, object]) -> str:
    """Format a payload as one Server-Sent Events ``data:`` frame."""

    return f"data: {json.dumps(payload)}\n\n"


async def _stream_chat_events(
    *,
    payload: ChatStreamRequestSchema,
    service: AIService,
    message_service: MessageService,
    assistant_message: ConversationMessage,
    context_messages: tuple[Message, ...],
) -> AsyncIterator[str]:
    """Yield SSE frames while streaming a chat completion into a conversation.

    Updates the assistant message's content after every chunk (per Sprint 6:
    "Assistant message content should be updated continuously") and marks it
    ``completed`` on success or ``failed`` on error -- the message is never
    deleted, only marked, so partial output remains visible in history.
    ``context_messages`` carries the full conversation history plus the new
    user message (per Sprint 7), built by :func:`_build_context_messages`.
    """

    accumulated_content = ""
    try:
        async for chunk in service.stream(
            messages=context_messages,
            model_alias=payload.model_alias,
            temperature=payload.temperature,
            system_prompt=payload.system_prompt,
        ):
            accumulated_content = chunk.content
            message_service.update_content_and_status(
                assistant_message.id,
                content=accumulated_content,
                status=MessageStatus.GENERATING,
            )
            yield _sse_event(
                {"type": "chunk", "delta": chunk.delta, "content": accumulated_content}
            )
    except Exception as exc:  # noqa: BLE001 - must not break the stream; reported below
        message_service.update_content_and_status(
            assistant_message.id,
            content=accumulated_content,
            status=MessageStatus.FAILED,
        )
        logger.exception(
            "ai_chat_stream_failed",
            conversation_id=str(payload.conversation_id),
            message_id=str(assistant_message.id),
        )
        error_code, error_message = _stream_error_payload(exc)
        yield _sse_event(
            {
                "type": "error",
                "success": False,
                "error": {"code": error_code, "message": error_message, "details": {}},
            }
        )
        return

    final_message = message_service.update_content_and_status(
        assistant_message.id,
        content=accumulated_content,
        status=MessageStatus.COMPLETED,
    )
    yield _sse_event(
        {
            "type": "done",
            "success": True,
            "message": "Chat completion generated successfully.",
            "data": {
                "message_id": str(final_message.id),
                "conversation_id": str(final_message.conversation_id),
                "status": final_message.status.value,
                "content": final_message.content,
            },
        }
    )


@router.post(
    "/chat/stream",
    summary="Generate a streaming chat completion",
)
async def post_chat_stream(
    payload: ChatStreamRequestSchema,
    service: Annotated[AIService, Depends(get_ai_service)],
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    message_service: Annotated[MessageService, Depends(get_message_service)],
) -> StreamingResponse:
    """Stream a chat completion token-by-token into a conversation.

    Unlike ``POST /chat``, ``conversation_id`` is required here: streaming
    exists specifically to update a conversation's assistant message in real
    time, so there is no "unchanged without one" behavior to preserve.

    Flow: validate the conversation exists (a missing/deleted conversation
    is rejected with the standard 404 error response before any streaming
    begins) -> load every existing message in the conversation (oldest
    first, no filtering or truncation) as context -> save the user's
    message -> create the assistant message with status ``generating`` ->
    stream chunks from :meth:`AIService.stream` (given the loaded context
    plus the new user message), updating that assistant message's content
    after every chunk -> mark it ``completed`` (or ``failed``, without
    deleting it, if generation raises) -> emit a final event with the saved
    message. Because the stream has already started with a 200 response by
    the time a failure can occur, failures are reported as a ``type:
    "error"`` event within the stream (using the same error code/message
    shape as the standard error envelope) rather than as an HTTP error
    status.

    ``POST /api/v1/ai/chat`` is unaffected by this endpoint and continues to
    work exactly as before.
    """

    conversation_service.get(payload.conversation_id)

    # Must run before persisting the new user message below, or that
    # message would be loaded as history and then appended again.
    context_messages = _build_context_messages(
        message_service, payload.conversation_id, payload.message
    )

    message_service.create(
        conversation_id=payload.conversation_id,
        role=MessageRole.USER,
        content=payload.message,
    )
    assistant_message = message_service.create(
        conversation_id=payload.conversation_id,
        role=MessageRole.ASSISTANT,
        content="",
        status=MessageStatus.GENERATING,
    )

    return StreamingResponse(
        _stream_chat_events(
            payload=payload,
            service=service,
            message_service=message_service,
            assistant_message=assistant_message,
            context_messages=context_messages,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
