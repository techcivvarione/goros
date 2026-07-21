"""API router definition for the LLM module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)
