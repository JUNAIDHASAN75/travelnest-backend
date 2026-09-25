from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.cost import CostCalculationResponse
from app.schemas.trip import TripCreate, TripResponse, TripUpdate
from app.services.cost_service import CostService
from app.services.trip_service import TripService

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trip plan"
)
def create_trip(
    request: TripCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return TripService.create_trip(db, request, current_user)


@router.get(
    "",
    response_model=List[TripResponse],
    summary="List all trips for the authenticated user"
)
def list_trips(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return TripService.list_user_trips(db, current_user, skip, limit)


@router.get(
    "/{id}",
    response_model=TripResponse,
    summary="Get trip details (user must own the trip)"
)
def get_trip(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return TripService.get_trip_or_404(db, id, current_user)


@router.put(
    "/{id}",
    response_model=TripResponse,
    summary="Update trip details"
)
def update_trip(
    id: int,
    request: TripUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return TripService.update_trip(db, id, request, current_user)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a trip"
)
def delete_trip(
    id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    TripService.delete_trip(db, id, current_user)


@router.post(
    "/{trip_id}/calculate-cost",
    response_model=CostCalculationResponse,
    summary="Calculate total cost breakdown for a trip"
)
def calculate_trip_cost(
    trip_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return CostService.calculate_trip_cost(db, trip_id, current_user)
