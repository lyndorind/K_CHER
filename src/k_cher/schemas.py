"""Pydantic-схеми запитів і відповідей."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CalculationCreate(BaseModel):
    operation: Literal["add", "divide"]
    a: float = Field(allow_inf_nan=False)
    b: float = Field(allow_inf_nan=False)


class CalculationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    operation: str
    a: float
    b: float
    result: float
    created_at: datetime
