from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class HotelBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Hotel name")
    address: str = Field(..., min_length=5, max_length=255, description="Street address")
    description: Optional[str] = None
    star_rating: int = Field(3, ge=1, le=5, description="Star rating between 1 and 5")
    image_url: Optional[str] = Field(None, max_length=500)


class HotelCreate(HotelBase):
    destination_id: int = Field(..., description="ID of associated destination")


class HotelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = None
    star_rating: Optional[int] = Field(None, ge=1, le=5)
    image_url: Optional[str] = Field(None, max_length=500)


class HotelResponse(HotelBase):
    id: int
    destination_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
