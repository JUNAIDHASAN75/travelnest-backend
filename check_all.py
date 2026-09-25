"""
Diagnostic script: checks all modules import correctly and counts API routes.
"""

errors = []

# 1. Core
try:
    from app.core.config import settings
    print("OK app.core.config")
except Exception as e:
    errors.append(f"FAIL app.core.config: {e}")

try:
    from app.core.database import engine, SessionLocal, Base, get_db
    print("OK app.core.database")
except Exception as e:
    errors.append(f"FAIL app.core.database: {e}")

try:
    from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, hash_token
    print("OK app.core.security")
except Exception as e:
    errors.append(f"FAIL app.core.security: {e}")

# 2. Models
try:
    from app.models.user import User, RefreshToken, UserRole
    print("OK app.models.user")
except Exception as e:
    errors.append(f"FAIL app.models.user: {e}")

try:
    from app.models.destination import Destination
    print("OK app.models.destination")
except Exception as e:
    errors.append(f"FAIL app.models.destination: {e}")

try:
    from app.models.activity import Activity
    print("OK app.models.activity")
except Exception as e:
    errors.append(f"FAIL app.models.activity: {e}")

try:
    from app.models.hotel import Hotel
    print("OK app.models.hotel")
except Exception as e:
    errors.append(f"FAIL app.models.hotel: {e}")

try:
    from app.models.room import Room
    print("OK app.models.room")
except Exception as e:
    errors.append(f"FAIL app.models.room: {e}")

try:
    from app.models.trip import Trip
    print("OK app.models.trip")
except Exception as e:
    errors.append(f"FAIL app.models.trip: {e}")

try:
    from app.models.booking import Booking, BookingStatus, BookingType
    print("OK app.models.booking")
except Exception as e:
    errors.append(f"FAIL app.models.booking: {e}")

try:
    from app.models.payment import Payment, PaymentStatus
    print("OK app.models.payment")
except Exception as e:
    errors.append(f"FAIL app.models.payment: {e}")

# 3. Schemas
try:
    from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
    print("OK app.schemas.auth")
except Exception as e:
    errors.append(f"FAIL app.schemas.auth: {e}")

try:
    from app.schemas.user import UserResponse, UserCreate, UserUpdate
    print("OK app.schemas.user")
except Exception as e:
    errors.append(f"FAIL app.schemas.user: {e}")

try:
    from app.schemas.destination import DestinationCreate, DestinationUpdate, DestinationResponse
    print("OK app.schemas.destination")
except Exception as e:
    errors.append(f"FAIL app.schemas.destination: {e}")

try:
    from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
    print("OK app.schemas.activity")
except Exception as e:
    errors.append(f"FAIL app.schemas.activity: {e}")

try:
    from app.schemas.hotel import HotelCreate, HotelUpdate, HotelResponse
    print("OK app.schemas.hotel")
except Exception as e:
    errors.append(f"FAIL app.schemas.hotel: {e}")

try:
    from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse
    print("OK app.schemas.room")
except Exception as e:
    errors.append(f"FAIL app.schemas.room: {e}")

try:
    from app.schemas.trip import TripCreate, TripUpdate, TripResponse
    print("OK app.schemas.trip")
except Exception as e:
    errors.append(f"FAIL app.schemas.trip: {e}")

try:
    from app.schemas.booking import BookingCreate, BookingResponse
    print("OK app.schemas.booking")
except Exception as e:
    errors.append(f"FAIL app.schemas.booking: {e}")

try:
    from app.schemas.cost import CostCalculationResponse, CostItem
    print("OK app.schemas.cost")
except Exception as e:
    errors.append(f"FAIL app.schemas.cost: {e}")

# 4. Services
try:
    from app.services.auth_service import AuthService
    print("OK app.services.auth_service")
except Exception as e:
    errors.append(f"FAIL app.services.auth_service: {e}")

try:
    from app.services.trip_service import TripService
    print("OK app.services.trip_service")
except Exception as e:
    errors.append(f"FAIL app.services.trip_service: {e}")

try:
    from app.services.booking_service import BookingService
    print("OK app.services.booking_service")
except Exception as e:
    errors.append(f"FAIL app.services.booking_service: {e}")

try:
    from app.services.cost_service import CostService
    print("OK app.services.cost_service")
except Exception as e:
    errors.append(f"FAIL app.services.cost_service: {e}")

# 5. API Routers
try:
    from app.api.deps import get_current_user, get_current_active_user, require_admin
    print("OK app.api.deps")
except Exception as e:
    errors.append(f"FAIL app.api.deps: {e}")

try:
    from app.api.v1.auth import router as auth_router
    print("OK app.api.v1.auth")
except Exception as e:
    errors.append(f"FAIL app.api.v1.auth: {e}")

try:
    from app.api.v1.users import router as users_router
    print("OK app.api.v1.users")
except Exception as e:
    errors.append(f"FAIL app.api.v1.users: {e}")

try:
    from app.api.v1.destinations import router as destinations_router
    print("OK app.api.v1.destinations")
except Exception as e:
    errors.append(f"FAIL app.api.v1.destinations: {e}")

try:
    from app.api.v1.hotels import router as hotels_router
    print("OK app.api.v1.hotels")
except Exception as e:
    errors.append(f"FAIL app.api.v1.hotels: {e}")

try:
    from app.api.v1.rooms import router as rooms_router
    print("OK app.api.v1.rooms")
except Exception as e:
    errors.append(f"FAIL app.api.v1.rooms: {e}")

try:
    from app.api.v1.activities import router as activities_router
    print("OK app.api.v1.activities")
except Exception as e:
    errors.append(f"FAIL app.api.v1.activities: {e}")

try:
    from app.api.v1.trips import router as trips_router
    print("OK app.api.v1.trips")
except Exception as e:
    errors.append(f"FAIL app.api.v1.trips: {e}")

try:
    from app.api.v1.bookings import router as bookings_router
    print("OK app.api.v1.bookings")
except Exception as e:
    errors.append(f"FAIL app.api.v1.bookings: {e}")

# 6. Main app
try:
    from main import app
    paths = list(app.openapi()["paths"].keys())
    print(f"OK main.py — {len(paths)} API paths registered")
except Exception as e:
    errors.append(f"FAIL main.py: {e}")

# 7. Database connectivity
try:
    from sqlalchemy import text
    with engine.connect() as conn:
        db_name = conn.execute(text("SELECT DATABASE()")).scalar()
    print(f"OK MySQL connection — connected to database: {db_name}")
except Exception as e:
    errors.append(f"FAIL MySQL connection: {e}")

# 8. Alembic migration check
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num"))
        versions = [row[0] for row in result]
    print(f"OK Alembic migrations applied: {versions}")
except Exception as e:
    errors.append(f"FAIL Alembic check: {e}")

# Summary
print()
if errors:
    print(f"=== ISSUES FOUND ({len(errors)}) ===")
    for err in errors:
        print(f"  {err}")
else:
    print(f"=== ALL CHECKS PASSED - No issues found ===")
