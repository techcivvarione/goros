"""API router definition for the MCP module."""

from fastapi import APIRouter

router = APIRouter(
    prefix="/mcp",
    tags=["MCP"],
)
