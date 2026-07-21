"""API router definition for the Audit module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)
