"""API router definition for the Memory module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)
