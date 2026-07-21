"""API router definition for the Usage module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/usage",
    tags=["Usage"],
)
