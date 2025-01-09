"""Pydantic models for game constraints."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ConstraintValue(BaseModel):
    """A single constraint value."""
    min_value: Optional[float] = Field(None, description="Minimum allowed value")
    max_value: Optional[float] = Field(None, description="Maximum allowed value")
    allowed_values: Optional[List[str]] = Field(None, description="List of allowed values")
    description: Optional[str] = Field(None, description="Description of the constraint")


class GameConstraints(BaseModel):
    """Collection of game constraints."""
    constraints: Dict[str, ConstraintValue] = Field(
        description="Map of constraint names to their values"
    )
