from datetime import date
from decimal import Decimal
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.booking import Booking, BookingStatus, BookingType
from app.models.room import Room
from app.models.trip import Trip
from app.models.user import User, UserRole
from app.schemas.booking import BookingCreate


class BookingService:
    @staticmethod
    def get_booking_or_404(db: Session, booking_id: int, user: User) -> Booking:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with ID {booking_id} not found"
            )
        if booking.user_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view or manage this booking"
            )
        return booking

    @staticmethod
    def list_user_bookings(db: Session, user: User, skip: int = 0, limit: int = 20) -> List[Booking]:
        query = db.query(Booking)
        if user.role != UserRole.ADMIN:
            query = query.filter(Booking.user_id == user.id)
        return query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def create_booking(db: Session, req: BookingCreate, user: User) -> Booking:
        # Validate trip association if provided
        if req.trip_id is not None:
            trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
            if not trip:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Associated trip ID {req.trip_id} does not exist"
                )
            if trip.user_id != user.id and user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot attach booking to a trip you do not own"
                )

        calculated_price = Decimal("0.00")

        # Atomic transaction
        try:
            if req.booking_type == BookingType.HOTEL:
                room = db.query(Room).filter(Room.id == req.item_id).with_for_update().first()
                if not room:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Room with ID {req.item_id} not found"
                    )
                if not room.is_available:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Selected room is currently unavailable"
                    )
                # Calculate nights
                nights = 1
                if req.start_date and req.end_date:
                    delta = (req.end_date - req.start_date).days
                    nights = max(1, delta)
                calculated_price = room.price_per_night * Decimal(nights)

            elif req.booking_type == BookingType.ACTIVITY:
                activity = db.query(Activity).filter(Activity.id == req.item_id).first()
                if not activity:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Activity with ID {req.item_id} not found"
                    )
                calculated_price = activity.price

            else:
                calculated_price = Decimal("100.00")

            new_booking = Booking(
                user_id=user.id,
                trip_id=req.trip_id,
                booking_type=req.booking_type,
                item_id=req.item_id,
                status=BookingStatus.CONFIRMED,
                total_price=calculated_price,
                start_date=req.start_date,
                end_date=req.end_date,
                special_requests=req.special_requests
            )
            db.add(new_booking)
            db.commit()
            db.refresh(new_booking)
            return new_booking

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transaction failed while creating booking"
            )

    @staticmethod
    def cancel_booking(db: Session, booking_id: int, user: User) -> Booking:
        booking = BookingService.get_booking_or_404(db, booking_id, user)

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled"
            )

        if booking.status == BookingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel an already completed booking"
            )

        try:
            booking.status = BookingStatus.CANCELLED
            db.commit()
            db.refresh(booking)
            return booking
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update booking status"
            )
