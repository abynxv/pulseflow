from typing import Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: float = Field(ge=0)
    unit_price: float = Field(ge=0)
    total: float = Field(ge=0)


class Invoice(BaseModel):
    vendor_name: str
    invoice_number: str
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    bill_to: Optional[str] = None
    line_items: list[LineItem] = []
    subtotal: Optional[float] = Field(default=None, ge=0)
    tax_rate: Optional[float] = Field(default=None, ge=0, le=1)
    tax_amount: Optional[float] = Field(default=None, ge=0)
    total_amount: float = Field(ge=0)
    currency: str = "USD"
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
