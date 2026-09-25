from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import BookingStatus, BookingType


class BookingBase(BaseModel):
    booking_type: BookingType = Field(..., description="Type: hotel, activity, or package")
    item_id: int = Field(..., description="ID of room or activity being booked")
    trip_id: Optional[int] = Field(None, description="Optional association with a trip plan")
    start_date: Optional[date] = Field(None, description="Check-in or activity date")
    end_date: Optional[date] = Field(None, description="Check-out date")
    special_requests: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: BookingStatus
    total_price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
