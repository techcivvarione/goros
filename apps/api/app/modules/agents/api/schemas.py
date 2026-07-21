"""Pydantic schemas for the Agents module."""

from typing import Literal

from pydantic import BaseModel, Field


class AgentsModuleSchema(BaseModel):
    """Base schema namespace for the Agents module."""

    module: Literal["agents"] = Field(
        default="agents",
        description="Stable module identifier.",
    )
