"""Pydantic schemas for the Organizations module."""

from typing import Literal

from pydantic import BaseModel, Field


class OrganizationsModuleSchema(BaseModel):
    """Base schema namespace for the Organizations module."""

    module: Literal["organizations"] = Field(
        default="organizations",
        description="Stable module identifier.",
    )
