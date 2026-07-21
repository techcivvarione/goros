"""API router definition for the Chat module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)
