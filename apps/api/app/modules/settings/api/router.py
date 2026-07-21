"""API router definition for the Settings module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/settings",
    tags=["Settings"],
)
