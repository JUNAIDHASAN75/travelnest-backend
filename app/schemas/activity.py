from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Activity title")
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0, description="Price per participant")
    duration_hours: Optional[float] = Field(None, gt=0, description="Estimated duration in hours")
    location: Optional[str] = Field(None, max_length=255, description="Specific location or meeting point")


class ActivityCreate(ActivityBase):
    destination_id: int = Field(..., description="ID of associated destination")


class ActivityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    duration_hours: Optional[float] = Field(None, gt=0)
    location: Optional[str] = Field(None, max_length=255)


class ActivityResponse(ActivityBase):
    id: int
    destination_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
