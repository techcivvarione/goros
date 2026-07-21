"""API router definition for the Models module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/models",
    tags=["Models"],
)
