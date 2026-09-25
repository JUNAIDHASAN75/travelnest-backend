from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking (transactional)"
)
def create_booking(
    request: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return BookingService.create_booking(db, request, current_user)


@router.get(
    "",
    response_model=List[BookingResponse],
    summary="List all bookings for current user"
)
def list_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return BookingService.list_user_bookings(db, current_user, skip, limit)


@router.get(
    "/{id}",
    response_model=BookingResponse,
    summary="Get booking details (user must own booking)"
)
def get_booking(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return BookingService.get_booking_or_404(db, id, current_user)


@router.patch(
    "/{id}/cancel",
    response_model=BookingResponse,
    summary="Cancel a booking (transactional)"
)
def cancel_booking(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return BookingService.cancel_booking(db, id, current_user)
