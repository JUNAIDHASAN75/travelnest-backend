from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.destination import Destination
from app.models.trip import Trip
from app.models.user import User, UserRole
from app.schemas.trip import TripCreate, TripUpdate


class TripService:
    @staticmethod
    def get_trip_or_404(db: Session, trip_id: int, user: User) -> Trip:
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip with ID {trip_id} not found"
            )
        # Verify ownership (unless admin)
        if trip.user_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this trip"
            )
        return trip

    @staticmethod
    def list_user_trips(db: Session, user: User, skip: int = 0, limit: int = 20) -> List[Trip]:
        query = db.query(Trip)
        if user.role != UserRole.ADMIN:
            query = query.filter(Trip.user_id == user.id)
        return query.order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_trip(db: Session, req: TripCreate, user: User) -> Trip:
        # Check destination exists
        dest = db.query(Destination).filter(Destination.id == req.destination_id).first()
        if not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination with ID {req.destination_id} not found"
            )

        new_trip = Trip(
            user_id=user.id,
            destination_id=req.destination_id,
            title=req.title.strip(),
            start_date=req.start_date,
            end_date=req.end_date,
            number_of_travelers=req.number_of_travelers,
            budget=req.budget,
            notes=req.notes.strip() if req.notes else None
        )
        db.add(new_trip)
        db.commit()
        db.refresh(new_trip)
        return new_trip

    @staticmethod
    def update_trip(db: Session, trip_id: int, req: TripUpdate, user: User) -> Trip:
        trip = TripService.get_trip_or_404(db, trip_id, user)

        if req.destination_id is not None:
            dest = db.query(Destination).filter(Destination.id == req.destination_id).first()
            if not dest:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Destination with ID {req.destination_id} not found"
                )
            trip.destination_id = req.destination_id

        if req.title is not None:
            trip.title = req.title.strip()
        if req.start_date is not None:
            trip.start_date = req.start_date
        if req.end_date is not None:
            trip.end_date = req.end_date
        if req.number_of_travelers is not None:
            trip.number_of_travelers = req.number_of_travelers
        if req.budget is not None:
            trip.budget = req.budget
        if req.notes is not None:
            trip.notes = req.notes.strip()

        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def delete_trip(db: Session, trip_id: int, user: User) -> None:
        trip = TripService.get_trip_or_404(db, trip_id, user)
        db.delete(trip)
        db.commit()
