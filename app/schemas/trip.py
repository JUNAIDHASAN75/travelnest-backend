from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class TripBase(BaseModel):
    destination_id: int = Field(..., description="Destination ID")
    title: str = Field(..., min_length=2, max_length=200, description="Trip title")
    start_date: date = Field(..., description="Start date of trip")
    end_date: date = Field(..., description="End date of trip")
    number_of_travelers: int = Field(1, ge=1, le=50, description="Number of travelers")
    budget: Optional[Decimal] = Field(None, ge=0, description="Target budget")
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    destination_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    number_of_travelers: Optional[int] = Field(None, ge=1, le=50)
    budget: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class TripResponse(TripBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
