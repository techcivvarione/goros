"""Pydantic schemas for the MCP module."""

from typing import Literal

from pydantic import BaseModel, Field


class McpModuleSchema(BaseModel):
    """Base schema namespace for the MCP module."""

    module: Literal["mcp"] = Field(
        default="mcp",
        description="Stable module identifier.",
    )
