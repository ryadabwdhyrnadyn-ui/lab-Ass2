# lab-Ass2 — Campus Room Booking Service

## 1. API Design

| Operation | Method | URI | Request Body | Success Status | Error Status Codes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Create room | `POST` | `/rooms` | `{"id": "B205", "building": "Engineering", "capacity": 40}` | `201 Created` | `409 Conflict`, `422 Unprocessable Entity` |
| List rooms | `GET` | `/rooms` | None | `200 OK` | None |
| Create booking | `POST` | `/bookings` | `{"room_id": "B205", "day": "2026-12-01", "start_hour": 10, "end_hour": 12, "purpose": "Study group"}` | `201 Created` | `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity` |
| Idempotent booking by client ID | `PUT` | `/bookings/{booking_id}` | `{"room_id": "B205", "day": "2026-12-01", "start_hour": 10, "end_hour": 12, "purpose": "Study group"}` | `200 OK` | `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity` |
| Delete booking | `DELETE` | `/bookings/{booking_id}` | None | `204 No Content` | `404 Not Found` |

## 2. Safe Retry Design (Idempotency)
Using `PUT /bookings/{booking_id}` with a client-chosen `booking_id` makes booking creation safe to retry. In HTTP, `PUT` is idempotent: if the server processes the request and creates the booking under `booking_id`, but the response is lost before reaching the client, resending the exact same request with the same `booking_id` and payload returns the existing booking without creating a second duplicate booking.

## 3. Client Script Output (`test_bookings.py`)
- POST /rooms (create B205) -> 201
- POST /rooms (duplicate B205) -> 409
- GET /rooms -> 200
- POST /bookings (unknown room) -> 404
- POST /bookings (end_hour <= start_hour) -> 422
- POST /bookings (10 to 12) -> 201
- POST /bookings (adjacent 12 to 13) -> 201
- POST /bookings (overlapping 11 to 13) -> 409
- PUT /bookings/CLIENT-BK-1 (retry x2) -> first=200, second=200, stored_count=1
- DELETE /bookings/CLIENT-BK-1 -> 204
- DELETE /bookings/CLIENT-BK-1 (not found) -> 404
