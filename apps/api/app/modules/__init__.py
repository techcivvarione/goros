"""GOROS application modules and router registry."""

from fastapi import APIRouter

from app.modules.admin import router as admin_router
from app.modules.agents import router as agents_router
from app.modules.api_keys import router as api_keys_router
from app.modules.audit import router as audit_router
from app.modules.billing import router as billing_router
from app.modules.chat import router as chat_router
from app.modules.conversations import router as conversations_router
from app.modules.documents import router as documents_router
from app.modules.embeddings import router as embeddings_router
from app.modules.identity import router as identity_router
from app.modules.integrations import router as integrations_router
from app.modules.knowledge import router as knowledge_router
from app.modules.llm import router as llm_router
from app.modules.mcp import router as mcp_router
from app.modules.memory import router as memory_router
from app.modules.models import router as models_router
from app.modules.organizations import router as organizations_router
from app.modules.prompts import router as prompts_router
from app.modules.rag import router as rag_router
from app.modules.settings import router as settings_router
from app.modules.system import router as system_router
from app.modules.tools import router as tools_router
from app.modules.usage import router as usage_router
from app.modules.users import router as users_router
from app.modules.webhooks import router as webhooks_router

PUBLIC_ROUTERS: tuple[APIRouter, ...] = (system_router,)

VERSIONED_ROUTERS: tuple[APIRouter, ...] = (
    identity_router,
    organizations_router,
    users_router,
    conversations_router,
    chat_router,
    prompts_router,
    agents_router,
    memory_router,
    knowledge_router,
    documents_router,
    rag_router,
    embeddings_router,
    llm_router,
    models_router,
    tools_router,
    mcp_router,
    usage_router,
    billing_router,
    api_keys_router,
    integrations_router,
    webhooks_router,
    audit_router,
    settings_router,
    admin_router,
)

__all__ = ["PUBLIC_ROUTERS", "VERSIONED_ROUTERS"]
