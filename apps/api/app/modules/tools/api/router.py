"""API router definition for the Tools module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
)
