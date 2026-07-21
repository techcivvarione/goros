"""Pydantic schemas for the Conversations module."""

from typing import Literal

from pydantic import BaseModel, Field


class ConversationsModuleSchema(BaseModel):
    """Base schema namespace for the Conversations module."""

    module: Literal["conversations"] = Field(
        default="conversations",
        description="Stable module identifier.",
    )
