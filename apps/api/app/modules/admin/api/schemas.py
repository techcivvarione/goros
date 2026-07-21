"""Pydantic schemas for the Admin module."""

from typing import Literal

from pydantic import BaseModel, Field


class AdminModuleSchema(BaseModel):
    """Base schema namespace for the Admin module."""

    module: Literal["admin"] = Field(
        default="admin",
        description="Stable module identifier.",
    )
