"""Pydantic schemas for the Identity module."""

from typing import Literal

from pydantic import BaseModel, Field


class IdentityModuleSchema(BaseModel):
    """Base schema namespace for the Identity module."""

    module: Literal["identity"] = Field(
        default="identity",
        description="Stable module identifier.",
    )
