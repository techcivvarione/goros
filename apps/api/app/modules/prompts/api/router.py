"""API router definition for the Prompts module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/prompts",
    tags=["Prompts"],
)
