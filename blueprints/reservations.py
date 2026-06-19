from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from helpers import (
    create_reservation,
    get_page,
    get_reservation_form,
    get_wedding_hall_map,
    update_reservation,
    validate_reservation,
)
from models import STATUS_APPROVED, STATUS_NOT_APPROVED, Reservation, WeddingHall

bp = Blueprint("reservations", __name__)

RESERVATIONS_PER_PAGE = 8


def reservation_sort_key(reservation, sort):
    if sort == "couple":
        return reservation.bride_name
    if sort == "hall":
        return reservation.wedding_hall.name
    if sort == "guest_count":
        return reservation.guest_count
    if sort == "status":
        return reservation.status
    if sort == "price":
        return reservation.price
    return reservation.date


def filter_reservations(reservations, search, hall_id, status, date_from, date_to):
    result = reservations

    if search:
        filtered = []
        for reservation in result:
            hall = reservation.wedding_hall
            if (
                search in reservation.bride_name
                or search in reservation.groom_name
                or search in hall.name
                or search in hall.location
            ):
                filtered.append(reservation)
        result = filtered

    if hall_id:
        filtered = []
        for reservation in result:
            if reservation.wedding_hall.id == hall_id:
                filtered.append(reservation)
        result = filtered

    if status in (STATUS_APPROVED, STATUS_NOT_APPROVED):
        filtered = []
        for reservation in result:
            if reservation.status == status:
                filtered.append(reservation)
        result = filtered

    if date_from:
        filtered = []
        for reservation in result:
            if reservation.date >= date_from:
                filtered.append(reservation)
        result = filtered

    if date_to:
        filtered = []
        for reservation in result:
            if reservation.date <= date_to:
                filtered.append(reservation)
        result = filtered

    return result


def paginate_list(items, page, per_page):
    total_items = len(items)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = min(page, total_pages)
    start = (page - 1) * per_page
    page_items = items[start:start + per_page]
    pagination = {"page": page, "total_pages": total_pages, "total_items": total_items}
    return page_items, pagination


def get_halls_sorted():
    halls = list(WeddingHall.select())

    def hall_name(hall):
        return hall.name

    halls.sort(key=hall_name)
    return halls


def flash_first_error(errors):
    for error_message in errors.values():
        flash(error_message, "error")
        break


@bp.route("/reservations")
def reservations_index():
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "date")
    order = request.args.get("order", "asc")
    page = get_page(request.args.get("page", "1"))
    status = request.args.get("status", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    hall_id_raw = request.args.get("hall_id", "").strip()
    hall_id = None
    if hall_id_raw:
        try:
            hall_id = int(hall_id_raw)
        except ValueError:
            hall_id_raw = ""

    if sort not in ("couple", "hall", "date", "guest_count", "status", "price"):
        sort = "date"
    if order not in ("asc", "desc"):
        order = "asc"

    reservations = list(Reservation.select())
    reservations = filter_reservations(
        reservations, search, hall_id, status, date_from, date_to
    )

    def sort_value(reservation):
        return reservation_sort_key(reservation, sort)

    reservations.sort(key=sort_value, reverse=(order == "desc"))
    reservations, pagination = paginate_list(reservations, page, RESERVATIONS_PER_PAGE)

    return render_template(
        "reservations/index.html",
        reservations=reservations,
        hall_map=get_wedding_hall_map(),
        search=search,
        filters={
            "status": status,
            "date_from": date_from,
            "date_to": date_to,
            "hall_id": str(hall_id) if hall_id else "",
        },
        sorting={"sort": sort, "order": order},
        pagination=pagination,
    )


@bp.route("/reservations/create", methods=["GET", "POST"])
def reservation_create():
    halls = get_halls_sorted()
    form_data = None
    form_errors = None

    if request.method == "POST":
        form_data = get_reservation_form(request.form)
        hall_id = int(form_data["wedding_hall_id"])
        hall = WeddingHall.get(id=hall_id)
        errors = validate_reservation(form_data, hall, hall_id)

        if errors:
            form_errors = errors
            flash_first_error(errors)
        else:
            create_reservation(hall, form_data)
            flash("Rezervacija je uspješno dodana.", "success")
            return redirect(url_for("reservations.reservations_index"))

    return render_template(
        "reservations/form.html",
        reservation=None,
        halls=halls,
        form_data=form_data,
        form_errors=form_errors,
        allow_past_date=False,
    )


@bp.route("/reservations/<int:reservation_id>/edit", methods=["GET", "POST"])
def reservation_edit(reservation_id):
    reservation = Reservation.get(id=reservation_id)
    if reservation is None:
        flash("Rezervacija nije pronađena.", "error")
        return redirect(url_for("reservations.reservations_index"))

    halls = get_halls_sorted()
    form_data = None
    form_errors = None

    if request.method == "POST":
        form_data = get_reservation_form(request.form)
        hall_id = int(form_data["wedding_hall_id"])
        hall = WeddingHall.get(id=hall_id)
        errors = validate_reservation(form_data, hall, hall_id, reservation_id)

        if errors:
            form_errors = errors
            flash_first_error(errors)
        else:
            update_reservation(reservation, hall, form_data)
            flash("Rezervacija je uspješno ažurirana.", "success")
            return redirect(url_for("reservations.reservations_index"))

    allow_past_date = reservation.date < date.today().isoformat()
    return render_template(
        "reservations/form.html",
        reservation=reservation,
        halls=halls,
        form_data=form_data,
        form_errors=form_errors,
        allow_past_date=allow_past_date,
    )


@bp.route("/reservations/<int:reservation_id>/delete", methods=["POST"])
def reservation_delete(reservation_id):
    reservation = Reservation.get(id=reservation_id)
    if reservation:
        reservation.delete()
        flash("Rezervacija je obrisana.", "success")
    return redirect(url_for("reservations.reservations_index"))
