"""API router definition for the Conversations module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)
