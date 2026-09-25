from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.booking import Booking, BookingStatus, BookingType
from app.models.room import Room
from app.models.trip import Trip
from app.models.user import User
from app.schemas.cost import CostCalculationResponse, CostItem
from app.services.trip_service import TripService


class CostService:
    TAX_RATE = Decimal("0.10")  # 10% taxes and service fees

    @staticmethod
    def calculate_trip_cost(db: Session, trip_id: int, user: User) -> CostCalculationResponse:
        trip = TripService.get_trip_or_404(db, trip_id, user)

        # Retrieve active (non-cancelled) bookings for this trip
        bookings = (
            db.query(Booking)
            .filter(Booking.trip_id == trip.id, Booking.status != BookingStatus.CANCELLED)
            .all()
        )

        cost_items: List[CostItem] = []
        category_totals: Dict[str, Decimal] = {
            "accommodation": Decimal("0.00"),
            "activity": Decimal("0.00"),
            "other": Decimal("0.00")
        }

        subtotal = Decimal("0.00")

        for b in bookings:
            if b.booking_type == BookingType.HOTEL:
                room = db.query(Room).filter(Room.id == b.item_id).first()
                item_name = f"Accommodation: {room.room_type if room else 'Hotel Room'}"
                cat = "accommodation"
                nights = 1
                if b.start_date and b.end_date:
                    delta = (b.end_date - b.start_date).days
                    nights = max(1, delta)

                item = CostItem(
                    name=item_name,
                    category=cat,
                    quantity=nights,
                    unit_price=b.total_price / Decimal(nights) if nights > 0 else b.total_price,
                    total_price=b.total_price
                )
            elif b.booking_type == BookingType.ACTIVITY:
                activity = db.query(Activity).filter(Activity.id == b.item_id).first()
                item_name = f"Activity: {activity.name if activity else 'Booked Activity'}"
                cat = "activity"
                item = CostItem(
                    name=item_name,
                    category=cat,
                    quantity=1,
                    unit_price=b.total_price,
                    total_price=b.total_price
                )
            else:
                cat = "other"
                item = CostItem(
                    name="Trip Expense",
                    category=cat,
                    quantity=1,
                    unit_price=b.total_price,
                    total_price=b.total_price
                )

            cost_items.append(item)
            category_totals[cat] += b.total_price
            subtotal += b.total_price

        # Monetary calculation with Decimal rounding
        taxes_and_fees = (subtotal * CostService.TAX_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = (subtotal + taxes_and_fees).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return CostCalculationResponse(
            trip_id=trip.id,
            currency="USD",
            subtotal=subtotal.quantize(Decimal("0.01")),
            taxes_and_fees=taxes_and_fees,
            total=total,
            cost_breakdown=cost_items,
            category_totals={k: v.quantize(Decimal("0.01")) for k, v in category_totals.items()}
        )
