"""Pydantic schemas for the Api Keys module."""

from typing import Literal

from pydantic import BaseModel, Field


class ApiKeysModuleSchema(BaseModel):
    """Base schema namespace for the Api Keys module."""

    module: Literal["api_keys"] = Field(
        default="api_keys",
        description="Stable module identifier.",
    )
