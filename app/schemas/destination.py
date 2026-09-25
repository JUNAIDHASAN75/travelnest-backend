from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DestinationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150, description="Destination title/name")
    country: str = Field(..., min_length=2, max_length=100, description="Country name")
    city: Optional[str] = Field(None, max_length=100, description="City name")
    description: Optional[str] = Field(None, description="Detailed overview of destination")
    image_url: Optional[str] = Field(None, max_length=500, description="Cover image URL")


class DestinationCreate(DestinationBase):
    pass


class DestinationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    country: Optional[str] = Field(None, min_length=2, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)


class DestinationResponse(DestinationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
