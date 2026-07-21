"""API router definition for the Api Keys module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/api_keys",
    tags=["Api Keys"],
)
