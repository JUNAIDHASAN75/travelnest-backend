from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.destination import Destination
from app.models.user import User
from app.schemas.destination import DestinationCreate, DestinationResponse, DestinationUpdate

router = APIRouter(prefix="/destinations", tags=["Destinations"])


@router.get(
    "",
    response_model=List[DestinationResponse],
    summary="List destinations with search, filter, and pagination"
)
def list_destinations(
    search: Optional[str] = Query(None, description="Search by destination name or city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Max results per page"),
    db: Session = Depends(get_db)
):
    query = db.query(Destination)
    if country:
        query = query.filter(Destination.country.ilike(f"%{country.strip()}%"))
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            (Destination.name.ilike(search_fmt)) | (Destination.city.ilike(search_fmt))
        )
    return query.order_by(Destination.name.asc()).offset(skip).limit(limit).all()


@router.get(
    "/{id}",
    response_model=DestinationResponse,
    summary="Get destination by ID"
)
def get_destination(
    id: int,
    db: Session = Depends(get_db)
):
    dest = db.query(Destination).filter(Destination.id == id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {id} not found"
        )
    return dest


@router.post(
    "",
    response_model=DestinationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new destination (Admin only)"
)
def create_destination(
    request: DestinationCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dest = Destination(
        name=request.name.strip(),
        country=request.country.strip(),
        city=request.city.strip() if request.city else None,
        description=request.description.strip() if request.description else None,
        image_url=request.image_url.strip() if request.image_url else None
    )
    db.add(dest)
    db.commit()
    db.refresh(dest)
    return dest


@router.put(
    "/{id}",
    response_model=DestinationResponse,
    summary="Update destination (Admin only)"
)
def update_destination(
    id: int,
    request: DestinationUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dest = db.query(Destination).filter(Destination.id == id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {id} not found"
        )

    if request.name is not None:
        dest.name = request.name.strip()
    if request.country is not None:
        dest.country = request.country.strip()
    if request.city is not None:
        dest.city = request.city.strip()
    if request.description is not None:
        dest.description = request.description.strip()
    if request.image_url is not None:
        dest.image_url = request.image_url.strip()

    db.commit()
    db.refresh(dest)
    return dest


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete destination (Admin only)"
)
def delete_destination(
    id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dest = db.query(Destination).filter(Destination.id == id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {id} not found"
        )
    db.delete(dest)
    db.commit()
