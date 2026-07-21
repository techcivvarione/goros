"""API router definition for the Integrations module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)
