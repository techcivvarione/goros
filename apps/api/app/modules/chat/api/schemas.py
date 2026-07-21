"""Pydantic schemas for the Chat module."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatModuleSchema(BaseModel):
    """Base schema namespace for the Chat module."""

    module: Literal["chat"] = Field(
        default="chat",
        description="Stable module identifier.",
    )
