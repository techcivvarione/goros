"""Pydantic schemas for the Tools module."""

from typing import Literal

from pydantic import BaseModel, Field


class ToolsModuleSchema(BaseModel):
    """Base schema namespace for the Tools module."""

    module: Literal["tools"] = Field(
        default="tools",
        description="Stable module identifier.",
    )
