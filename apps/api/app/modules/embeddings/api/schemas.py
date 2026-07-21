"""Pydantic schemas for the Embeddings module."""

from typing import Literal

from pydantic import BaseModel, Field


class EmbeddingsModuleSchema(BaseModel):
    """Base schema namespace for the Embeddings module."""

    module: Literal["embeddings"] = Field(
        default="embeddings",
        description="Stable module identifier.",
    )
