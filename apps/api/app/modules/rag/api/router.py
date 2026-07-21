"""API router definition for the Rag module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/rag",
    tags=["Rag"],
)
