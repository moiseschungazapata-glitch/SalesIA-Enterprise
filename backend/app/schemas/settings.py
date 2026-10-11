"""Commercial configuration contracts."""

from decimal import Decimal

from pydantic import BaseModel, Field


class CommercialSettingsResponse(BaseModel):
    tax_rate: Decimal
    prices_include_tax: bool
    max_discount_percent: Decimal


class CommercialSettingsUpdate(BaseModel):
    tax_rate: Decimal = Field(ge=0, le=100)
    prices_include_tax: bool
    max_discount_percent: Decimal = Field(ge=0, le=100)
