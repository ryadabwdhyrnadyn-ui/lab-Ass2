import httpx

BASE_URL = "http://127.0.0.1:8001"


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        r = client.post("/rooms", json={"id": "B205", "building": "Engineering", "capacity": 40})
        print("POST /rooms (create B205) ->", r.status_code)

        r = client.post("/rooms", json={"id": "B205", "building": "Engineering", "capacity": 40})
        print("POST /rooms (duplicate B205) ->", r.status_code)

        r = client.get("/rooms")
        print("GET /rooms ->", r.status_code)

        r = client.post(
            "/bookings",
            json={"room_id": "UNKNOWN", "day": "2026-12-01", "start_hour": 10, "end_hour": 12, "purpose": "Study group"},
        )
        print("POST /bookings (unknown room) ->", r.status_code)

        r = client.post(
            "/bookings",
            json={"room_id": "B205", "day": "2026-12-01", "start_hour": 14, "end_hour": 12, "purpose": "Bad hours"},
        )
        print("POST /bookings (end_hour <= start_hour) ->", r.status_code)

        r = client.post(
            "/bookings",
            json={"room_id": "B205", "day": "2026-12-01", "start_hour": 10, "end_hour": 12, "purpose": "Study group"},
        )
        print("POST /bookings (10 to 12) ->", r.status_code)

        r = client.post(
            "/bookings",
            json={"room_id": "B205", "day": "2026-12-01", "start_hour": 12, "end_hour": 13, "purpose": "Extra lab"},
        )
        print("POST /bookings (adjacent 12 to 13) ->", r.status_code)

        r = client.post(
            "/bookings",
            json={"room_id": "B205", "day": "2026-12-01", "start_hour": 11, "end_hour": 13, "purpose": "Overlap"},
        )
        print("POST /bookings (overlapping 11 to 13) ->", r.status_code)

        idem_body = {
            "room_id": "B205",
            "day": "2026-12-02",
            "start_hour": 9,
            "end_hour": 11,
            "purpose": "Team meeting",
        }
        r1 = client.put("/bookings/CLIENT-BK-1", json=idem_body)
        r2 = client.put("/bookings/CLIENT-BK-1", json=idem_body)
        all_bookings = client.get("/bookings").json()
        matches = [b for b in all_bookings if b["booking_id"] == "CLIENT-BK-1"]
        print(f"PUT /bookings/CLIENT-BK-1 (retry x2) -> first={r1.status_code}, second={r2.status_code}, stored_count={len(matches)}")

        r = client.delete("/bookings/CLIENT-BK-1")
        print("DELETE /bookings/CLIENT-BK-1 ->", r.status_code)

        r = client.delete("/bookings/CLIENT-BK-1")
        print("DELETE /bookings/CLIENT-BK-1 (not found) ->", r.status_code)


if __name__ == "__main__":
    main()
