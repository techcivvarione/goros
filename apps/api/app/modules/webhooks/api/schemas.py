"""Pydantic schemas for the Webhooks module."""

from typing import Literal

from pydantic import BaseModel, Field


class WebhooksModuleSchema(BaseModel):
    """Base schema namespace for the Webhooks module."""

    module: Literal["webhooks"] = Field(
        default="webhooks",
        description="Stable module identifier.",
    )
