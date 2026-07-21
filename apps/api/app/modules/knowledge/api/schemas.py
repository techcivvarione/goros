"""Pydantic schemas for the Knowledge module."""

from typing import Literal

from pydantic import BaseModel, Field


class KnowledgeModuleSchema(BaseModel):
    """Base schema namespace for the Knowledge module."""

    module: Literal["knowledge"] = Field(
        default="knowledge",
        description="Stable module identifier.",
    )
