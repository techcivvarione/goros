"""API router definition for the Organizations module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)
