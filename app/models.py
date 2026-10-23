import re
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProductShelfLifeRequest(BaseModel):
    ean: str = Field(..., min_length=1)
    product_name: str = Field(..., min_length=1)
    product_category: str = Field(..., min_length=1)
    mrp: float = Field(..., ge=0)
    batch_no: str = Field(..., min_length=1)
    mfg_date: str
    exp_date: str
    shelf_life_days: int = Field(..., ge=0)
    shelf_life_basis: str = Field(..., min_length=1)
    storage_conditions: str = Field(..., min_length=1)
    packaging_type: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    remarks: Optional[str] = None

    @field_validator("ean")
    @classmethod
    def validate_ean(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("EAN must contain only digits")
        return value

    @field_validator("mfg_date", "exp_date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("Date must be in YYYY-MM-DD format")
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date: {value}")
        return value
