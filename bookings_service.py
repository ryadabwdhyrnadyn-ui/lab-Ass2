from datetime import date
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Campus Room Booking Service - lab-Ass2")


class Room(BaseModel):
    id: str = Field(min_length=2, max_length=20)
    building: str = Field(min_length=2, max_length=80)
    capacity: int = Field(ge=1, le=1000)


class BookingCreate(BaseModel):
    room_id: str = Field(min_length=2, max_length=20)
    day: date
    start_hour: int = Field(ge=8, le=20)
    end_hour: int = Field(ge=8, le=20)
    purpose: str = Field(min_length=3, max_length=200)

    @model_validator(mode="after")
    def validate_hours(self) -> "BookingCreate":
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be greater than start_hour")
        return self


class Booking(BookingCreate):
    booking_id: str


rooms: dict[str, Room] = {}
bookings: dict[str, Booking] = {}
seq: int = 1


def has_overlap(
    room_id: str,
    day: date,
    start_hour: int,
    end_hour: int,
    ignore_booking_id: str | None = None,
) -> bool:
    for b in bookings.values():
        if ignore_booking_id is not None and b.booking_id == ignore_booking_id:
            continue
        if b.room_id == room_id and b.day == day:
            if start_hour < b.end_hour and end_hour > b.start_hour:
                return True
    return False


@app.post("/rooms", status_code=201)
def create_room(room: Room) -> Room:
    if room.id in rooms:
        raise HTTPException(status_code=409, detail=f"Room {room.id} already exists")
    rooms[room.id] = room
    return room


@app.get("/rooms")
def list_rooms() -> list[Room]:
    return list(rooms.values())


@app.post("/bookings", status_code=201)
def create_booking(payload: BookingCreate) -> Booking:
    global seq
    if payload.room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {payload.room_id} not found")
    if has_overlap(payload.room_id, payload.day, payload.start_hour, payload.end_hour):
        raise HTTPException(status_code=409, detail="Booking overlaps with an existing booking")

    booking_id = f"B-{seq}"
    seq += 1
    booking = Booking(booking_id=booking_id, **payload.model_dump())
    bookings[booking_id] = booking
    return booking


@app.put("/bookings/{booking_id}", status_code=200)
def upsert_booking(booking_id: str, payload: BookingCreate) -> Booking:
    if payload.room_id not in rooms:
        raise HTTPException(status_code=404, detail=f"Room {payload.room_id} not found")

    existing = bookings.get(booking_id)
    if existing is not None and existing.model_dump(exclude={"booking_id"}) == payload.model_dump():
        return existing

    if has_overlap(
        payload.room_id,
        payload.day,
        payload.start_hour,
        payload.end_hour,
        ignore_booking_id=booking_id,
    ):
        raise HTTPException(status_code=409, detail="Booking overlaps with an existing booking")

    booking = Booking(booking_id=booking_id, **payload.model_dump())
    bookings[booking_id] = booking
    return booking


@app.get("/bookings")
def list_bookings() -> list[Booking]:
    return list(bookings.values())


@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: str) -> Response:
    if booking_id not in bookings:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    del bookings[booking_id]
    return Response(status_code=204)
