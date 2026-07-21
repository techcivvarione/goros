"""Pydantic schemas for the Documents module."""

from typing import Literal

from pydantic import BaseModel, Field


class DocumentsModuleSchema(BaseModel):
    """Base schema namespace for the Documents module."""

    module: Literal["documents"] = Field(
        default="documents",
        description="Stable module identifier.",
    )
