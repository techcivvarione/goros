"""API router definition for the Documents module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)
