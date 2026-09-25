# TravelNest Backend — Complete Architecture & Operations Manual

This document details the production-ready architecture, security configurations, database schemas, and end-to-end usage instructions for the TravelNest travel booking API.

---

## 1. Final Folder Structure

```text
travelnest-backend/
│
├── alembic/                               # Alembic database migrations
│   ├── versions/
│   │   ├── 76a7ecff7ef2_create_users_and_refresh_tokens_tables.py
│   │   └── 97ce9cd468ca_create_destinations_hotels_activities_.py
│   ├── env.py                             # Migration runner wired to settings.DATABASE_URL
│   └── script.py.mako
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                      # Pydantic Settings (.env, JWT, CORS)
│   │   ├── database.py                    # SQLAlchemy 2.x engine, SessionLocal, get_db
│   │   └── security.py                    # Argon2id password hasher & JWT manager
│   │
│   ├── models/
│   │   ├── __init__.py                    # Model registry for Alembic discovery
│   │   ├── user.py                        # User & RefreshToken models
│   │   ├── destination.py                 # Destination model
│   │   ├── activity.py                    # Activity model
│   │   ├── hotel.py                       # Hotel model
│   │   ├── room.py                        # Room model
│   │   ├── trip.py                        # Trip model
│   │   ├── booking.py                     # Booking model (status & type enums)
│   │   └── payment.py                     # Payment metadata schema
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                        # Register, Login, Token, Refresh schemas
│   │   ├── user.py                        # User response, update schemas
│   │   ├── destination.py                 # Destination CRUD schemas
│   │   ├── activity.py                    # Activity schemas
│   │   ├── hotel.py                       # Hotel schemas
│   │   ├── room.py                        # Room schemas
│   │   ├── trip.py                        # Trip schemas (start/end date validators)
│   │   ├── booking.py                     # Booking schemas
│   │   └── cost.py                        # Itemized cost breakdown schemas
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                        # get_current_user, get_current_active_user, require_admin
│   │   └── v1/
│   │       ├── __init__.py                # Consolidates all v1 routers
│   │       ├── auth.py                    # /api/v1/auth (register, login, refresh, logout, me)
│   │       ├── users.py                   # /api/v1/users (profile & admin CRUD)
│   │       ├── destinations.py            # /api/v1/destinations (public read, admin write)
│   │       ├── hotels.py                  # /api/v1/hotels & hotel rooms
│   │       ├── rooms.py                   # /api/v1/rooms (direct room updates)
│   │       ├── activities.py              # /api/v1/activities (public read, admin write)
│   │       ├── trips.py                   # /api/v1/trips (user-owned trip plans & calculate-cost)
│   │       └── bookings.py                # /api/v1/bookings (transactional creation & cancellation)
│   │
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py                # Authentication, password hashing, token rotation
│       ├── trip_service.py                # Trip ownership validation and CRUD
│       ├── booking_service.py             # Transactional booking & cancellation
│       └── cost_service.py                # Decimal-based itemized cost calculation
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                        # In-memory SQLite fixture & TestClient
│   ├── test_auth.py                       # Auth unit/integration tests
│   └── test_travel_features.py            # Destination, Hotel, Trip, Booking & Cost tests
│
├── .env                                   # Secret environment variables (ignored by git)
├── .env.example                           # Configuration template
├── .gitignore                             # Ignores .env, caches, virtualenv
├── alembic.ini                            # Migration configuration
├── ENDPOINTS.md                           # Master API reference grouped by domain
├── HOW_IT_WORKS.md                        # Architectural and operational guide
├── main.py                                # Application entry point, CORS & router mounting
├── pytest.ini                             # Pytest discovery configuration
└── requirements.txt                       # Locked dependencies
```

---

## 2. All Active API Endpoints

### System & Health
- `GET /` — API health check
- `GET /db-test` — MySQL database connectivity check
- `GET /docs` — Swagger UI interactive documentation
- `GET /redoc` — ReDoc documentation

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` — Register a new user
- `POST /api/v1/auth/login` — Log in and get JWT access & refresh tokens
- `POST /api/v1/auth/refresh` — Rotate refresh token for a fresh token pair
- `POST /api/v1/auth/logout` — Revoke active refresh token
- `GET  /api/v1/auth/me` — Profile of current logged-in user

### User Management (`/api/v1/users`)
- `GET    /api/v1/users/me` — Current user profile
- `PUT    /api/v1/users/me` — Update current user profile
- `GET    /api/v1/users` — List all users *(Admin only)*
- `GET    /api/v1/users/{id}` — Get user details *(Admin only)*
- `DELETE /api/v1/users/{id}` — Remove/deactivate user *(Admin only)*

### Destinations (`/api/v1/destinations`)
- `GET    /api/v1/destinations` — List destinations (supports `search`, `country`, pagination)
- `GET    /api/v1/destinations/{id}` — Get single destination
- `POST   /api/v1/destinations` — Add destination *(Admin only)*
- `PUT    /api/v1/destinations/{id}` — Update destination *(Admin only)*
- `DELETE /api/v1/destinations/{id}` — Delete destination *(Admin only)*

### Hotels & Rooms (`/api/v1/hotels` & `/api/v1/rooms`)
- `GET    /api/v1/hotels` — List hotels (supports `destination_id`, `min_stars`, pagination)
- `GET    /api/v1/hotels/{id}` — Get hotel details
- `POST   /api/v1/hotels` — Create hotel *(Admin only)*
- `PUT    /api/v1/hotels/{id}` — Update hotel *(Admin only)*
- `DELETE /api/v1/hotels/{id}` — Delete hotel *(Admin only)*
- `GET    /api/v1/hotels/{hotel_id}/rooms` — List rooms in a hotel
- `POST   /api/v1/hotels/{hotel_id}/rooms` — Add room to hotel *(Admin only)*
- `PUT    /api/v1/rooms/{id}` — Update room details *(Admin only)*
- `DELETE /api/v1/rooms/{id}` — Delete room *(Admin only)*

### Activities (`/api/v1/activities`)
- `GET    /api/v1/activities` — List activities (supports `destination_id` filter)
- `GET    /api/v1/activities/{id}` — Get activity details
- `POST   /api/v1/activities` — Create activity *(Admin only)*
- `PUT    /api/v1/activities/{id}` — Update activity *(Admin only)*
- `DELETE /api/v1/activities/{id}` — Delete activity *(Admin only)*

### Trips (`/api/v1/trips`)
- `POST   /api/v1/trips` — Create a trip plan
- `GET    /api/v1/trips` — List user's trips
- `GET    /api/v1/trips/{id}` — Get trip details *(ownership verified)*
- `PUT    /api/v1/trips/{id}` — Update trip *(ownership verified)*
- `DELETE /api/v1/trips/{id}` — Delete trip *(ownership verified)*
- `POST   /api/v1/trips/{trip_id}/calculate-cost` — Itemized cost calculation breakdown

### Bookings (`/api/v1/bookings`)
- `POST   /api/v1/bookings` — Create a booking *(transactional with row locking)*
- `GET    /api/v1/bookings` — List user's bookings
- `GET    /api/v1/bookings/{id}` — Get booking details *(ownership verified)*
- `PATCH  /api/v1/bookings/{id}/cancel` — Cancel a booking *(transactional)*

---

## 3. Required Environment Variables

Configured in [.env](file:///d:/Cloud%20House%20Projects/backend/travelnest-backend/.env):

```env
# Database Credentials
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=GameWithPassion$01
DB_NAME=travelnest

# Security & JWT
JWT_SECRET_KEY=8e41258eefb2f58084f7954f83d2392b92d11a0cb4df19a4117274ad5f944abe
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000
```

---

## 4. Installation & Setup Commands

Activate your virtual environment and install dependencies:
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## 5. Database Migration Commands

Apply migrations to MySQL:
```powershell
.\venv\Scripts\alembic upgrade head
```

To create a new migration after modifying models:
```powershell
.\venv\Scripts\alembic revision --autogenerate -m "describe changes"
.\venv\Scripts\alembic upgrade head
```

---

## 6. How to Run the Server

```powershell
.\venv\Scripts\uvicorn main:app --reload --port 8000
```
Interactive docs:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 7. How to Test Authentication

### A. Register
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Sarah Connor",
       "email": "sarah@example.com",
       "password": "SecurePassword123!"
     }'
```

### B. Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "sarah@example.com",
       "password": "SecurePassword123!"
     }'
```
Response:
```json
{
  "access_token": "ey...",
  "refresh_token": "ey...",
  "token_type": "bearer"
}
```

---

## 8. How to Test Protected Endpoints

Pass the access token in the `Authorization` header:
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

In Swagger UI (`/docs`), click the green **Authorize** button at the top right, paste `YOUR_ACCESS_TOKEN`, and click **Authorize**.

---

## 9. Security Considerations

1. **Argon2id Hashing**: Password hashing uses memory-hard parameters resisting brute-force and GPU crack attacks.
2. **Refresh Token Rotation**: Each refresh token is single-use. When exchanged, the old token is permanently revoked, and only a SHA-256 hash is persisted.
3. **Strict Authorization**: User ownership is strictly verified against the decoded JWT subject (`current_user.id`), ignoring any client-supplied spoofed user IDs.
4. **Transactions & Race Conditions**: Room bookings utilize database transactions with row-level locks to prevent double-booking.
5. **No Floating Point Arithmetic for Money**: Prices and cost calculations use Python's `Decimal` and SQL `Numeric(10,2)`.
6. **No Secrets in Source Control**: `.env` is ignored by `.gitignore`.

---

## 10. Automated Tests

Run the safe, in-memory SQLite test suite:
```powershell
.\venv\Scripts\pytest -v
```
Output:
```text
tests/test_auth.py::test_register_user_success PASSED
tests/test_auth.py::test_register_duplicate_email_fails PASSED
tests/test_auth.py::test_login_success_and_me PASSED
tests/test_auth.py::test_login_invalid_password PASSED
tests/test_auth.py::test_unauthorized_request PASSED
tests/test_auth.py::test_refresh_token_and_logout PASSED
tests/test_travel_features.py::test_destination_crud_and_admin_protection PASSED
tests/test_travel_features.py::test_hotel_and_room_creation PASSED
tests/test_travel_features.py::test_trip_ownership_and_cost_calculation PASSED
======================== 9 passed in 3.09s ========================
```
