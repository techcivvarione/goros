"""API router definition for the Agents module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/agents",
    tags=["Agents"],
)
