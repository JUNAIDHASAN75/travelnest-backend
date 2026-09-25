from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.destination import Destination
from app.models.hotel import Hotel
from app.models.room import Room
from app.models.user import User
from app.schemas.hotel import HotelCreate, HotelResponse, HotelUpdate
from app.schemas.room import RoomCreate, RoomResponse

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get(
    "",
    response_model=List[HotelResponse],
    summary="List hotels (filter by destination or star rating)"
)
def list_hotels(
    destination_id: Optional[int] = Query(None, description="Filter by destination ID"),
    min_stars: Optional[int] = Query(None, ge=1, le=5, description="Filter by minimum star rating"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Hotel)
    if destination_id:
        query = query.filter(Hotel.destination_id == destination_id)
    if min_stars:
        query = query.filter(Hotel.star_rating >= min_stars)
    return query.order_by(Hotel.name.asc()).offset(skip).limit(limit).all()


@router.get(
    "/{id}",
    response_model=HotelResponse,
    summary="Get hotel by ID"
)
def get_hotel(
    id: int,
    db: Session = Depends(get_db)
):
    hotel = db.query(Hotel).filter(Hotel.id == id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with ID {id} not found"
        )
    return hotel


@router.post(
    "",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new hotel (Admin only)"
)
def create_hotel(
    request: HotelCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dest = db.query(Destination).filter(Destination.id == request.destination_id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {request.destination_id} not found"
        )

    hotel = Hotel(
        destination_id=request.destination_id,
        name=request.name.strip(),
        address=request.address.strip(),
        description=request.description.strip() if request.description else None,
        star_rating=request.star_rating,
        image_url=request.image_url.strip() if request.image_url else None
    )
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return hotel


@router.put(
    "/{id}",
    response_model=HotelResponse,
    summary="Update hotel details (Admin only)"
)
def update_hotel(
    id: int,
    request: HotelUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    hotel = db.query(Hotel).filter(Hotel.id == id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with ID {id} not found"
        )

    if request.name is not None:
        hotel.name = request.name.strip()
    if request.address is not None:
        hotel.address = request.address.strip()
    if request.description is not None:
        hotel.description = request.description.strip()
    if request.star_rating is not None:
        hotel.star_rating = request.star_rating
    if request.image_url is not None:
        hotel.image_url = request.image_url.strip()

    db.commit()
    db.refresh(hotel)
    return hotel


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete hotel (Admin only)"
)
def delete_hotel(
    id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    hotel = db.query(Hotel).filter(Hotel.id == id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with ID {id} not found"
        )
    db.delete(hotel)
    db.commit()


# Sub-routes for Hotel Rooms
@router.get(
    "/{hotel_id}/rooms",
    response_model=List[RoomResponse],
    summary="List all rooms for a specific hotel"
)
def list_hotel_rooms(
    hotel_id: int,
    db: Session = Depends(get_db)
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with ID {hotel_id} not found"
        )
    return hotel.rooms


@router.post(
    "/{hotel_id}/rooms",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a room to a hotel (Admin only)"
)
def add_room_to_hotel(
    hotel_id: int,
    request: RoomCreate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with ID {hotel_id} not found"
        )

    room = Room(
        hotel_id=hotel_id,
        room_type=request.room_type.strip(),
        description=request.description.strip() if request.description else None,
        price_per_night=request.price_per_night,
        capacity=request.capacity,
        is_available=request.is_available
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room
