"""API router definition for the Users module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)
