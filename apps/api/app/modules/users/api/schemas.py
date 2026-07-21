"""Pydantic schemas for the Users module."""

from typing import Literal

from pydantic import BaseModel, Field


class UsersModuleSchema(BaseModel):
    """Base schema namespace for the Users module."""

    module: Literal["users"] = Field(
        default="users",
        description="Stable module identifier.",
    )
