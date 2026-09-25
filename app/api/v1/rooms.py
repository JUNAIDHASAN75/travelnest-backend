from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.room import Room
from app.models.user import User
from app.schemas.room import RoomResponse, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.put(
    "/{id}",
    response_model=RoomResponse,
    summary="Update room details (Admin only)"
)
def update_room(
    id: int,
    request: RoomUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {id} not found"
        )

    if request.room_type is not None:
        room.room_type = request.room_type.strip()
    if request.description is not None:
        room.description = request.description.strip()
    if request.price_per_night is not None:
        room.price_per_night = request.price_per_night
    if request.capacity is not None:
        room.capacity = request.capacity
    if request.is_available is not None:
        room.is_available = request.is_available

    db.commit()
    db.refresh(room)
    return room


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a room (Admin only)"
)
def delete_room(
    id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {id} not found"
        )
    db.delete(room)
    db.commit()
