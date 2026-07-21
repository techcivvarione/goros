"""API router definition for the Conversations module."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.conversations.api.schemas import (
    ConversationCreateRequest,
    ConversationResponseData,
    MessageResponseData,
)
from app.modules.conversations.application.conversation_service import (
    ConversationService,
)
from app.modules.conversations.application.message_service import MessageService
from app.modules.conversations.domain.entities import Conversation, ConversationMessage
from app.modules.conversations.infrastructure.message_repository import (
    MessageRepository,
)
from app.modules.conversations.infrastructure.repository import ConversationRepository
from app.shared import SuccessResponse, success_response

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


def get_conversation_service(
    session: Annotated[Session, Depends(get_db)],
) -> ConversationService:
    """Build the conversation service for the current request-scoped session."""

    repository = ConversationRepository(session)
    return ConversationService(repository)


def get_message_service(
    session: Annotated[Session, Depends(get_db)],
) -> MessageService:
    """Build the message service for the current request-scoped session."""

    repository = MessageRepository(session)
    return MessageService(repository)


def _to_response_data(conversation: Conversation) -> ConversationResponseData:
    """Translate a domain entity into its API response schema."""

    return ConversationResponseData(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        is_deleted=conversation.is_deleted,
        metadata=conversation.metadata,
    )


def _to_message_response_data(message: ConversationMessage) -> MessageResponseData:
    """Translate a message domain entity into its API response schema."""

    return MessageResponseData(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        status=message.status,
        created_at=message.created_at,
        metadata=message.metadata,
    )


@router.post(
    "",
    response_model=SuccessResponse[ConversationResponseData],
    status_code=status.HTTP_201_CREATED,
    summary="Create a conversation",
)
async def create_conversation(
    payload: ConversationCreateRequest,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> SuccessResponse[ConversationResponseData]:
    """Create a new conversation, generating a title if none is supplied."""

    conversation = service.create(title=payload.title)
    return success_response(
        message="Conversation created successfully.",
        data=_to_response_data(conversation),
    )


@router.get(
    "",
    response_model=SuccessResponse[list[ConversationResponseData]],
    summary="List conversations",
)
async def list_conversations(
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> SuccessResponse[list[ConversationResponseData]]:
    """Return all non-deleted conversations."""

    conversations = service.list()
    return success_response(
        message="Conversations retrieved successfully.",
        data=[_to_response_data(conversation) for conversation in conversations],
    )


@router.get(
    "/{conversation_id}",
    response_model=SuccessResponse[ConversationResponseData],
    summary="Get a conversation",
)
async def get_conversation(
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> SuccessResponse[ConversationResponseData]:
    """Return a single non-deleted conversation.

    Raises the standard error response (404) via the global exception
    handlers if the conversation does not exist or has been soft-deleted.
    """

    conversation = service.get(conversation_id)
    return success_response(
        message="Conversation retrieved successfully.",
        data=_to_response_data(conversation),
    )


@router.delete(
    "/{conversation_id}",
    response_model=SuccessResponse[ConversationResponseData],
    summary="Soft delete a conversation",
)
async def delete_conversation(
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> SuccessResponse[ConversationResponseData]:
    """Soft-delete a conversation and return its updated state.

    Raises the standard error response (404) via the global exception
    handlers if the conversation does not exist or has already been
    soft-deleted.
    """

    conversation = service.delete(conversation_id)
    return success_response(
        message="Conversation deleted successfully.",
        data=_to_response_data(conversation),
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=SuccessResponse[list[MessageResponseData]],
    summary="List messages for a conversation",
)
async def list_conversation_messages(
    conversation_id: UUID,
    conversation_service: Annotated[
        ConversationService, Depends(get_conversation_service)
    ],
    message_service: Annotated[MessageService, Depends(get_message_service)],
) -> SuccessResponse[list[MessageResponseData]]:
    """Return all messages for a conversation, ordered oldest first.

    Raises the standard error response (404) via the global exception
    handlers if the conversation does not exist or has been soft-deleted.
    """

    conversation_service.get(conversation_id)
    messages = message_service.list_by_conversation(conversation_id)
    return success_response(
        message="Messages retrieved successfully.",
        data=[_to_message_response_data(message) for message in messages],
    )
