"""Pydantic schemas for the Audit module."""

from typing import Literal

from pydantic import BaseModel, Field


class AuditModuleSchema(BaseModel):
    """Base schema namespace for the Audit module."""

    module: Literal["audit"] = Field(
        default="audit",
        description="Stable module identifier.",
    )
