from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.destinations import router as destinations_router
from app.api.v1.hotels import router as hotels_router
from app.api.v1.rooms import router as rooms_router
from app.api.v1.activities import router as activities_router
from app.api.v1.trips import router as trips_router
from app.api.v1.bookings import router as bookings_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(destinations_router)
api_v1_router.include_router(hotels_router)
api_v1_router.include_router(rooms_router)
api_v1_router.include_router(activities_router)
api_v1_router.include_router(trips_router)
api_v1_router.include_router(bookings_router)
