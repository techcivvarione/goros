"""Pydantic schemas for the Billing module."""

from typing import Literal

from pydantic import BaseModel, Field


class BillingModuleSchema(BaseModel):
    """Base schema namespace for the Billing module."""

    module: Literal["billing"] = Field(
        default="billing",
        description="Stable module identifier.",
    )
