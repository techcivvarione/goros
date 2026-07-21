"""Pydantic schemas for the Usage module."""

from typing import Literal

from pydantic import BaseModel, Field


class UsageModuleSchema(BaseModel):
    """Base schema namespace for the Usage module."""

    module: Literal["usage"] = Field(
        default="usage",
        description="Stable module identifier.",
    )
