"""Pydantic schemas for the Prompts module."""

from typing import Literal

from pydantic import BaseModel, Field


class PromptsModuleSchema(BaseModel):
    """Base schema namespace for the Prompts module."""

    module: Literal["prompts"] = Field(
        default="prompts",
        description="Stable module identifier.",
    )
