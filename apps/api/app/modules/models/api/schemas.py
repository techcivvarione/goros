"""Pydantic schemas for the Models module."""

from typing import Literal

from pydantic import BaseModel, Field


class ModelsModuleSchema(BaseModel):
    """Base schema namespace for the Models module."""

    module: Literal["models"] = Field(
        default="models",
        description="Stable module identifier.",
    )
