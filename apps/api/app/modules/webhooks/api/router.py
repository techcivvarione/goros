"""API router definition for the Webhooks module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)
