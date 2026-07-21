"""API router definition for the Knowledge module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)
