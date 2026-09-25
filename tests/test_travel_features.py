from decimal import Decimal
from app.models.user import User, UserRole
from app.core.security import hash_password, create_access_token


def get_auth_headers(client, email="traveler@example.com", role=UserRole.USER):
    # Register & get token
    password = "StrongPassword123!"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": email, "password": password}
    )
    # Login
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_admin_headers(db_session):
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password_hash=hash_password("AdminPass123!"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    token = create_access_token(subject=str(admin.id), role="admin")
    return {"Authorization": f"Bearer {token}"}


def test_destination_crud_and_admin_protection(client, db_session):
    admin_headers = get_admin_headers(db_session)
    user_headers = get_auth_headers(client, email="regular@example.com")

    # Regular user cannot create destination (403)
    unauth_create = client.post(
        "/api/v1/destinations",
        json={"name": "Bali", "country": "Indonesia", "city": "Denpasar"},
        headers=user_headers
    )
    assert unauth_create.status_code == 403

    # Admin creates destination (201)
    create_res = client.post(
        "/api/v1/destinations",
        json={"name": "Kyoto", "country": "Japan", "city": "Kyoto"},
        headers=admin_headers
    )
    assert create_res.status_code == 201
    dest_id = create_res.json()["id"]

    # Public can view destinations
    list_res = client.get("/api/v1/destinations")
    assert list_res.status_code == 200
    assert any(d["name"] == "Kyoto" for d in list_res.json())

    # Get single destination
    get_res = client.get(f"/api/v1/destinations/{dest_id}")
    assert get_res.status_code == 200
    assert get_res.json()["country"] == "Japan"


def test_hotel_and_room_creation(client, db_session):
    admin_headers = get_admin_headers(db_session)

    # Create destination
    dest_res = client.post(
        "/api/v1/destinations",
        json={"name": "Paris", "country": "France", "city": "Paris"},
        headers=admin_headers
    )
    dest_id = dest_res.json()["id"]

    # Create hotel
    hotel_res = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": dest_id,
            "name": "Grand Palace Hotel",
            "address": "123 Champs Elysees",
            "star_rating": 5
        },
        headers=admin_headers
    )
    assert hotel_res.status_code == 201
    hotel_id = hotel_res.json()["id"]

    # Add room
    room_res = client.post(
        f"/api/v1/hotels/{hotel_id}/rooms",
        json={
            "room_type": "Deluxe Suite",
            "price_per_night": 250.00,
            "capacity": 2,
            "is_available": True
        },
        headers=admin_headers
    )
    assert room_res.status_code == 201
    assert room_res.json()["price_per_night"] == "250.00"

    # Public get rooms
    rooms_list = client.get(f"/api/v1/hotels/{hotel_id}/rooms")
    assert rooms_list.status_code == 200
    assert len(rooms_list.json()) == 1


def test_trip_ownership_and_cost_calculation(client, db_session):
    admin_headers = get_admin_headers(db_session)
    user1_headers = get_auth_headers(client, email="traveler1@example.com")
    user2_headers = get_auth_headers(client, email="traveler2@example.com")

    # Admin creates destination & room
    dest_res = client.post(
        "/api/v1/destinations",
        json={"name": "Rome", "country": "Italy", "city": "Rome"},
        headers=admin_headers
    )
    dest_id = dest_res.json()["id"]

    hotel_res = client.post(
        "/api/v1/hotels",
        json={
            "destination_id": dest_id,
            "name": "Roma Colosseo Hotel",
            "address": "Via dei Fori Imperiali",
            "star_rating": 4
        },
        headers=admin_headers
    )
    hotel_id = hotel_res.json()["id"]

    room_res = client.post(
        f"/api/v1/hotels/{hotel_id}/rooms",
        json={
            "room_type": "Standard Double",
            "price_per_night": 100.00,
            "capacity": 2,
            "is_available": True
        },
        headers=admin_headers
    )
    room_id = room_res.json()["id"]

    # User 1 creates trip
    trip_res = client.post(
        "/api/v1/trips",
        json={
            "destination_id": dest_id,
            "title": "Italian Vacation",
            "start_date": "2026-10-01",
            "end_date": "2026-10-04",
            "number_of_travelers": 2,
            "budget": 1500.00
        },
        headers=user1_headers
    )
    assert trip_res.status_code == 201
    trip_id = trip_res.json()["id"]

    # User 2 cannot access user 1's trip (403)
    forbidden_res = client.get(f"/api/v1/trips/{trip_id}", headers=user2_headers)
    assert forbidden_res.status_code == 403

    # User 1 creates booking attached to this trip (3 nights: Oct 1 to Oct 4 = $300)
    booking_res = client.post(
        "/api/v1/bookings",
        json={
            "trip_id": trip_id,
            "booking_type": "hotel",
            "item_id": room_id,
            "start_date": "2026-10-01",
            "end_date": "2026-10-04"
        },
        headers=user1_headers
    )
    assert booking_res.status_code == 201
    assert booking_res.json()["total_price"] == "300.00"

    # Calculate trip cost
    cost_res = client.post(f"/api/v1/trips/{trip_id}/calculate-cost", headers=user1_headers)
    assert cost_res.status_code == 200
    cost_data = cost_res.json()
    assert cost_data["subtotal"] == "300.00"
    assert cost_data["taxes_and_fees"] == "30.00"  # 10%
    assert cost_data["total"] == "330.00"
    assert len(cost_data["cost_breakdown"]) == 1

    # User 1 cancels booking
    booking_id = booking_res.json()["id"]
    cancel_res = client.patch(f"/api/v1/bookings/{booking_id}/cancel", headers=user1_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"
