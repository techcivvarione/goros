"""Pydantic schemas for the Integrations module."""

from typing import Literal

from pydantic import BaseModel, Field


class IntegrationsModuleSchema(BaseModel):
    """Base schema namespace for the Integrations module."""

    module: Literal["integrations"] = Field(
        default="integrations",
        description="Stable module identifier.",
    )
