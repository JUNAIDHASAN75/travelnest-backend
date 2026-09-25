from decimal import Decimal
from typing import Dict, List
from pydantic import BaseModel, Field


class CostItem(BaseModel):
    name: str
    category: str  # accommodation, activity, transport, taxes
    quantity: int = 1
    unit_price: Decimal
    total_price: Decimal


class CostCalculationResponse(BaseModel):
    trip_id: int
    currency: str = "USD"
    subtotal: Decimal
    taxes_and_fees: Decimal
    total: Decimal
    cost_breakdown: List[CostItem]
    category_totals: Dict[str, Decimal]
