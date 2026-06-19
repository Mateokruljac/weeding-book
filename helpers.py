from datetime import date

from pony.orm import desc, select

from models import Reservation, STATUS_APPROVED, STATUS_NOT_APPROVED, WeddingHall


def get_page(page_raw):
    try:
        return max(1, int(page_raw))
    except (TypeError, ValueError):
        return 1


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_wedding_hall_map():
    return {
        str(hall.id): f"{hall.name} ({hall.location})"
        for hall in select(h for h in WeddingHall).order_by(WeddingHall.name)
    }


def paginate(query, page, per_page=5):
    total_items = query.count()
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    items = list(query.limit(per_page, offset=offset))
    return items, {"page": page, "total_pages": total_pages, "total_items": total_items}


def sort_and_paginate(query, sort_map, sort, order, page, per_page=8):
    sort = sort if sort in sort_map else next(iter(sort_map))
    order = order if order in ("asc", "desc") else "asc"
    field = sort_map[sort]

    if order == "desc":
        query = query.order_by(lambda item: desc(field(item)))
    else:
        query = query.order_by(field)

    items, pagination = paginate(query, page, per_page)
    return items, pagination, sort, order


def date_taken(hall_id, reservation_date, reservation_id=None):
    hall_id = int(hall_id)
    query = select(
        r for r in Reservation
        if r.wedding_hall.id == hall_id
        and r.date == reservation_date
        and r.status == STATUS_APPROVED
    )
    if reservation_id is not None:
        query = query.filter(lambda r: r.id != int(reservation_id))
    return query.count() > 0


def wedding_hall_exists(name, location, hall_id=None):
    existing = WeddingHall.get(name=name, location=location)
    if not existing:
        return False
    return hall_id is None or existing.id != hall_id


def get_reservation_form(form):
    return {
        "date": form.get("date", "").strip(),
        "bride_name": form.get("bride_name", "").strip(),
        "groom_name": form.get("groom_name", "").strip(),
        "bride_contact": form.get("bride_contact", "").strip(),
        "groom_contact": form.get("groom_contact", "").strip(),
        "guest_count": form.get("guest_count", "").strip(),
        "status": form.get("status", STATUS_NOT_APPROVED).strip(),
        "wedding_hall_id": form.get("wedding_hall_id", "").strip(),
    }


def date_in_past(date_str, reservation_id=None):
    try:
        entered = date.fromisoformat(date_str)
    except ValueError:
        return False

    if entered >= date.today():
        return False

    if reservation_id:
        existing = Reservation.get(id=reservation_id)
        if existing and existing.date == date_str:
            return False

    return True


def validate_reservation(form_data, wedding_hall, hall_id, reservation_id=None):
    errors = {}

    required = {
        "bride_name": "Ime i prezime mladenke",
        "groom_name": "Ime i prezime mladozenje",
        "bride_contact": "Kontakt mladenke",
        "groom_contact": "Kontakt mladozenja",
    }
    for field, label in required.items():
        if not form_data.get(field):
            errors[field] = f"{label} je obavezno."

    reservation_date = form_data.get("date", "")
    if not reservation_date:
        errors["date"] = "Datum je obavezan."
    elif date_in_past(reservation_date, reservation_id):
        errors["date"] = "Datum ne smije biti u proslosti."
    else:
        try:
            date.fromisoformat(reservation_date)
        except ValueError:
            errors["date"] = "Unesite ispravan datum."
        if "date" not in errors and date_taken(hall_id, reservation_date, reservation_id):
            errors["date"] = (
                "Za taj datum vec postoji odobrena rezervacija za ovu salu. "
                "Odaberite drugi datum."
            )

    guest_raw = form_data.get("guest_count", "")
    if wedding_hall is None:
        errors["wedding_hall_id"] = "Odabrana sala ne postoji."
    else:
        try:
            guest_count = int(guest_raw)
            if guest_count < 1:
                errors["guest_count"] = "Broj gostiju mora biti najmanje 1."
            elif guest_count > wedding_hall.capacity:
                errors["guest_count"] = (
                    f"Broj gostiju ne smije premasivati kapacitet sale ({wedding_hall.capacity})."
                )
        except (TypeError, ValueError):
            if "guest_count" not in errors:
                errors["guest_count"] = "Unesite ispravan broj gostiju."

    status = form_data.get("status", "")
    if status not in {STATUS_APPROVED, STATUS_NOT_APPROVED}:
        errors["status"] = "Odaberite ispravan status."

    return errors


def serialize_reservation_for_calendar(reservation, edit_url):
    status = reservation.status
    return {
        "id": str(reservation.id),
        "title": f"{reservation.bride_name} i {reservation.groom_name}",
        "start": reservation.date,
        "classNames": ["fc-event-approved" if status == STATUS_APPROVED else "fc-event-pending"],
        "extendedProps": {
            "bride_name": reservation.bride_name,
            "groom_name": reservation.groom_name,
            "bride_contact": reservation.bride_contact,
            "groom_contact": reservation.groom_contact,
            "date": reservation.date,
            "status": status,
            "status_label": "Odobrena" if status == STATUS_APPROVED else "Nije odobrena",
            "guest_count": reservation.guest_count,
            "price": reservation.price,
            "edit_url": edit_url,
        },
    }


def get_hall_calendar_data(hall, edit_url_builder):
    reservations = sorted(hall.reservations, key=lambda r: r.date)
    events = [
        serialize_reservation_for_calendar(r, edit_url_builder(r.id))
        for r in reservations
    ]
    blocked_dates = sorted({r.date for r in reservations if r.status == STATUS_APPROVED})
    return {"events": events, "blocked_dates": blocked_dates, "total": len(reservations)}


def create_reservation(hall, form_data):
    return Reservation(
        wedding_hall=hall,
        bride_name=form_data["bride_name"],
        groom_name=form_data["groom_name"],
        bride_contact=form_data["bride_contact"],
        groom_contact=form_data["groom_contact"],
        date=form_data["date"],
        guest_count=int(form_data["guest_count"]),
        status=form_data["status"],
        price=hall.price,
    )


def update_reservation(reservation, hall, form_data):
    reservation.wedding_hall = hall
    reservation.bride_name = form_data["bride_name"]
    reservation.groom_name = form_data["groom_name"]
    reservation.bride_contact = form_data["bride_contact"]
    reservation.groom_contact = form_data["groom_contact"]
    reservation.date = form_data["date"]
    reservation.guest_count = int(form_data["guest_count"])
    reservation.status = form_data["status"]
    reservation.price = hall.price
