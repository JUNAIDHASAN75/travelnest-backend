# TravelNest API Endpoints

All application APIs are prefixed with `/api/v1` (except root system checks and OpenAPI documentation).

---

## 1. System & Health
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/` | Public | Root health check |
| `GET` | `/db-test` | Public | MySQL database connection test |
| `GET` | `/docs` | Public | Interactive Swagger UI API documentation |
| `GET` | `/redoc` | Public | ReDoc OpenAPI documentation |

---

## 2. Authentication (`/api/v1/auth`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Register a new user account |
| `POST` | `/api/v1/auth/login` | Public | Log in with email & password, returns JWT tokens |
| `POST` | `/api/v1/auth/refresh` | Public | Exchange refresh token for fresh access & rotated refresh token |
| `POST` | `/api/v1/auth/logout` | Public / User | Log out and revoke active refresh token |
| `GET` | `/api/v1/auth/me` | Authenticated User | Get current logged-in user profile |

---

## 3. Users (`/api/v1/users`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/users/me` | Authenticated User | Get current user's profile |
| `PUT` | `/api/v1/users/me` | Authenticated User | Update current user's profile |
| `GET` | `/api/v1/users` | Admin | List all users with pagination |
| `GET` | `/api/v1/users/{id}` | Admin | Get user details by user ID |
| `DELETE` | `/api/v1/users/{id}` | Admin | Deactivate/remove a user |

---

## 4. Destinations (`/api/v1/destinations`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/destinations` | Public | List destinations (with search, filter, pagination) |
| `GET` | `/api/v1/destinations/{id}` | Public | Get destination details by ID |
| `POST` | `/api/v1/destinations` | Admin | Create a new destination |
| `PUT` | `/api/v1/destinations/{id}` | Admin | Update existing destination |
| `DELETE` | `/api/v1/destinations/{id}` | Admin | Delete a destination |

---

## 5. Hotels & Rooms (`/api/v1/hotels` & `/api/v1/rooms`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/hotels` | Public | List hotels (filter by destination, rating, price) |
| `GET` | `/api/v1/hotels/{id}` | Public | Get hotel details by ID |
| `POST` | `/api/v1/hotels` | Admin | Add a new hotel |
| `PUT` | `/api/v1/hotels/{id}` | Admin | Update hotel details |
| `DELETE` | `/api/v1/hotels/{id}` | Admin | Delete a hotel |
| `GET` | `/api/v1/hotels/{hotel_id}/rooms` | Public | List available rooms for a hotel |
| `POST` | `/api/v1/hotels/{hotel_id}/rooms` | Admin | Add a room to a hotel |
| `PUT` | `/api/v1/rooms/{id}` | Admin | Update room details/pricing |
| `DELETE` | `/api/v1/rooms/{id}` | Admin | Delete a room |

---

## 6. Activities (`/api/v1/activities`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/activities` | Public | List activities (filter by destination/category) |
| `GET` | `/api/v1/activities/{id}` | Public | Get activity details by ID |
| `POST` | `/api/v1/activities` | Admin | Create a new activity |
| `PUT` | `/api/v1/activities/{id}` | Admin | Update activity details |
| `DELETE` | `/api/v1/activities/{id}` | Admin | Delete an activity |

---

## 7. Trips (`/api/v1/trips`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/trips` | Authenticated User | List current user's trips |
| `POST` | `/api/v1/trips` | Authenticated User | Create a new trip plan |
| `GET` | `/api/v1/trips/{id}` | Authenticated User | Get trip details (ownership verified) |
| `PUT` | `/api/v1/trips/{id}` | Authenticated User | Update trip details (dates, travelers, budget) |
| `DELETE` | `/api/v1/trips/{id}` | Authenticated User | Delete a trip |
| `POST` | `/api/v1/trips/{trip_id}/calculate-cost` | Authenticated User | Calculate total trip cost with itemized breakdown |

---

## 8. Bookings (`/api/v1/bookings`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/bookings` | Authenticated User | List current user's bookings |
| `POST` | `/api/v1/bookings` | Authenticated User | Create a new booking (transactional) |
| `GET` | `/api/v1/bookings/{id}` | Authenticated User | Get booking details (ownership verified) |
| `PATCH` | `/api/v1/bookings/{id}/cancel` | Authenticated User | Cancel a booking (transactional) |

---

## 9. Payments (`/api/v1/payments`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/payments/checkout-session` | Authenticated User | Create payment session / intent |
| `GET` | `/api/v1/payments/{id}` | Authenticated User | Check status of a payment |
