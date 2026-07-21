"""Pydantic schemas for the Rag module."""

from typing import Literal

from pydantic import BaseModel, Field


class RagModuleSchema(BaseModel):
    """Base schema namespace for the Rag module."""

    module: Literal["rag"] = Field(
        default="rag",
        description="Stable module identifier.",
    )
