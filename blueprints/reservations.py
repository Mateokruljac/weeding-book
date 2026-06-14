from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from pony.orm import select
from helpers import (
    create_reservation,
    get_page,
    get_reservation_form,
    get_wedding_hall_map,
    sort_and_paginate,
    update_reservation,
    validate_reservation,
)
from models import STATUS_APPROVED, STATUS_NOT_APPROVED, Reservation, WeddingHall

bp = Blueprint("reservations", __name__)

RESERVATION_SORT = {
    "couple": lambda r: r.bride_name,
    "hall": lambda r: r.wedding_hall.name,
    "date": lambda r: r.date,
    "guest_count": lambda r: r.guest_count,
    "status": lambda r: r.status,
    "price": lambda r: r.price,
}


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

    query = Reservation.select()
    if search:
        query = query.filter(
            lambda r: search in r.bride_name
            or search in r.groom_name
            or search in r.wedding_hall.name
            or search in r.wedding_hall.location
        )

    if hall_id:
        query = query.filter(lambda r: r.wedding_hall.id == hall_id)

    if status in (STATUS_APPROVED, STATUS_NOT_APPROVED):
        query = query.filter(lambda r: r.status == status)

    if date_from:
        query = query.filter(lambda r: r.date >= date_from)

    if date_to:
        query = query.filter(lambda r: r.date <= date_to)

    reservations, pagination, sort, order = sort_and_paginate(query, RESERVATION_SORT, sort, order, page)

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
    halls = select(h for h in WeddingHall).order_by(WeddingHall.name)
    form_data = None
    form_errors = None

    if request.method == "POST":
        form_data = get_reservation_form(request.form)
        hall_id = int(form_data["wedding_hall_id"])
        hall = WeddingHall.get(id=hall_id)
        errors = validate_reservation(form_data, hall, hall_id)

        if errors:
            form_errors = errors
            flash(next(iter(errors.values())), "error")
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

    halls = select(h for h in WeddingHall).order_by(WeddingHall.name)
    form_data = None
    form_errors = None

    if request.method == "POST":
        form_data = get_reservation_form(request.form)
        hall_id = int(form_data["wedding_hall_id"])
        hall = WeddingHall.get(id=hall_id)
        errors = validate_reservation(form_data, hall, hall_id, reservation_id)

        if errors:
            form_errors = errors
            flash(next(iter(errors.values())), "error")
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