"""Pydantic schemas for the LLM module."""

from typing import Literal

from pydantic import BaseModel, Field


class LlmModuleSchema(BaseModel):
    """Base schema namespace for the LLM module."""

    module: Literal["llm"] = Field(
        default="llm",
        description="Stable module identifier.",
    )
