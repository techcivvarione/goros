"""API router definition for the Billing module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/billing",
    tags=["Billing"],
)
