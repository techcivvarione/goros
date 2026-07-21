"""Pydantic schemas for the Settings module."""

from typing import Literal

from pydantic import BaseModel, Field


class SettingsModuleSchema(BaseModel):
    """Base schema namespace for the Settings module."""

    module: Literal["settings"] = Field(
        default="settings",
        description="Stable module identifier.",
    )
