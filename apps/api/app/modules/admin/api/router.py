"""API router definition for the Admin module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)
