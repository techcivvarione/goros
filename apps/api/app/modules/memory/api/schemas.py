"""Pydantic schemas for the Memory module."""

from typing import Literal

from pydantic import BaseModel, Field


class MemoryModuleSchema(BaseModel):
    """Base schema namespace for the Memory module."""

    module: Literal["memory"] = Field(
        default="memory",
        description="Stable module identifier.",
    )
