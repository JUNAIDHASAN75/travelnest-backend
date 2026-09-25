from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RoomBase(BaseModel):
    room_type: str = Field(..., min_length=2, max_length=100, description="e.g. Deluxe Suite, Standard Single")
    description: Optional[str] = None
    price_per_night: Decimal = Field(..., gt=0, description="Price per night")
    capacity: int = Field(2, ge=1, le=20, description="Max guests capacity")
    is_available: bool = Field(True, description="Availability status")


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_type: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price_per_night: Optional[Decimal] = Field(None, gt=0)
    capacity: Optional[int] = Field(None, ge=1, le=20)
    is_available: Optional[bool] = None


class RoomResponse(RoomBase):
    id: int
    hotel_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
