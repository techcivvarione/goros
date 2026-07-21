"""API router definition for the Identity module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/identity",
    tags=["Identity"],
)
