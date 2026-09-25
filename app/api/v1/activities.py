from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.activity import Activity
from app.models.destination import Destination
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityUpdate

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get(
    "",
    response_model=List[ActivityResponse],
    summary="List activities (with optional destination filter)"
)
def list_activities(
    destination_id: Optional[int] = Query(None, description="Filter activities by destination ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Activity)
    if destination_id:
        query = query.filter(Activity.destination_id == destination_id)
    return query.order_by(Activity.name.asc()).offset(skip).limit(limit).all()


@router.get(
    "/{id}",
    response_model=ActivityResponse,
    summary="Get activity details by ID"
)
def get_activity(
    id: int,
    db: Session = Depends(get_db)
):
    act = db.query(Activity).filter(Activity.id == id).first()
    if not act:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {id} not found"
        )
    return act


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new activity (Admin only)"
)
def create_activity(
    request: ActivityCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dest = db.query(Destination).filter(Destination.id == request.destination_id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {request.destination_id} not found"
        )

    act = Activity(
        destination_id=request.destination_id,
        name=request.name.strip(),
        description=request.description.strip() if request.description else None,
        price=request.price,
        duration_hours=request.duration_hours,
        location=request.location.strip() if request.location else None
    )
    db.add(act)
    db.commit()
    db.refresh(act)
    return act


@router.put(
    "/{id}",
    response_model=ActivityResponse,
    summary="Update activity (Admin only)"
)
def update_activity(
    id: int,
    request: ActivityUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    act = db.query(Activity).filter(Activity.id == id).first()
    if not act:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {id} not found"
        )

    if request.name is not None:
        act.name = request.name.strip()
    if request.description is not None:
        act.description = request.description.strip()
    if request.price is not None:
        act.price = request.price
    if request.duration_hours is not None:
        act.duration_hours = request.duration_hours
    if request.location is not None:
        act.location = request.location.strip()

    db.commit()
    db.refresh(act)
    return act


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete activity (Admin only)"
)
def delete_activity(
    id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    act = db.query(Activity).filter(Activity.id == id).first()
    if not act:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {id} not found"
        )
    db.delete(act)
    db.commit()
