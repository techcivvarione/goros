"""API router definition for the Embeddings module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"],
)
