from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from pony.orm import commit, desc, select
from helpers import (
    create_reservation,
    get_page,
    get_reservation_form,
    get_wedding_hall_map,
    paginate,
    sort_and_paginate,
    to_float,
    validate_reservation,
    wedding_hall_exists,
)
from models import Reservation, WeddingHall

bp = Blueprint("halls", __name__)

HALL_SORT = {
    "name": lambda h: h.name,
    "location": lambda h: h.location,
    "capacity": lambda h: h.capacity,
    "price": lambda h: h.price,
}

@bp.route("/halls")
def halls_index():
    if request.args.get("format") == "json":
        return jsonify(get_wedding_hall_map())

    search = request.args.get("search", "")
    sort = request.args.get("sort", "name")
    order = request.args.get("order", "asc")
    page = get_page(request.args.get("page", "1"))
    location = request.args.get("location", "")
    min_price = request.args.get("min_price", "")
    max_price = request.args.get("max_price", "")
    min_val = to_float(min_price)
    max_val = to_float(max_price)

    query = WeddingHall.select()
    if search:
        query = query.filter(lambda h: search in h.name or search in h.location)

    if location:
        query = query.filter(lambda h: location in h.location)

    if min_val is not None:
        query = query.filter(lambda h: h.price >= min_val)

    if max_val is not None:
        query = query.filter(lambda h: h.price <= max_val)

    halls, pagination, sort, order = sort_and_paginate(query, HALL_SORT, sort, order, page)

    return render_template(
        "halls/index.html",
        halls=halls,
        search=search,
        filters={"location": location, "min_price": min_price, "max_price": max_price},
        sorting={"sort": sort, "order": order},
        pagination=pagination,
    )


@bp.route("/halls/create", methods=["GET", "POST"])
def hall_create():
    if request.method == "POST":
        name = request.form["name"].strip()
        location = request.form["location"].strip()
        capacity = request.form["capacity"].strip()
        price = request.form["price"].strip()

        if not name or not location or not capacity or not price:
            flash("Sva polja za salu su obavezna.", "error")

        elif wedding_hall_exists(name, location):
            flash("Sala s tim nazivom i lokacijom već postoji.", "error")
        else:
            try:
                WeddingHall(
                    name=name,
                    location=location,
                    capacity=int(capacity),
                    price=float(price),
                )
                commit()

                flash("Sala je uspješno dodana.", "success")
                return redirect(url_for("halls.halls_index"))

            except ValueError:
                flash("Kapacitet i cijena moraju biti ispravni brojevi.", "error")

    return render_template("halls/form.html", hall=None)


@bp.route("/halls/<int:hall_id>/edit", methods=["GET", "POST"])
def hall_edit(hall_id):
    hall = WeddingHall.get(id=hall_id)
    if hall is None:
        flash("Sala nije pronađena.", "error")
        return redirect(url_for("halls.halls_index"))

    if request.method == "POST":
        name = request.form["name"].strip()
        location = request.form["location"].strip()
        capacity = request.form["capacity"].strip()
        price = request.form["price"].strip()

        if not name or not location or not capacity or not price:
            flash("Sva polja za salu su obavezna.", "error")

        elif wedding_hall_exists(name, location, hall_id):
            flash("Sala s tim nazivom i lokacijom već postoji.", "error")

        else:
            try:
                hall.name = name
                hall.location = location
                hall.capacity = int(capacity)
                hall.price = float(price)
                commit()
                flash("Sala je uspješno ažurirana.", "success")
                return redirect(url_for("halls.halls_index"))
            except ValueError:
                flash("Kapacitet i cijena moraju biti ispravni brojevi.", "error")

    res_page = get_page(request.args.get("page", "1"))
    res_query = select(r for r in Reservation if r.wedding_hall.id == hall_id).order_by(desc(Reservation.date))
    reservations, res_pagination = paginate(res_query, res_page, per_page=5)
    reservation_form = session.pop("reservation_form", None)
    reservation_errors = session.pop("reservation_errors", None)
    open_form = request.args.get("open_form") == "1" or bool(reservation_form)

    return render_template(
        "halls/form.html",
        hall=hall,
        reservations=reservations,
        res_pagination=res_pagination,
        open_form=open_form,
        reservation_form=reservation_form,
        reservation_errors=reservation_errors,
    )


@bp.route("/halls/<int:hall_id>/reservations/create", methods=["POST"])
def hall_reservation_create(hall_id):
    hall = WeddingHall.get(id=hall_id)
    if hall is None:
        flash("Sala nije pronađena.", "error")
        return redirect(url_for("halls.halls_index"))

    form_data = get_reservation_form(request.form)
    errors = validate_reservation(form_data, hall, hall_id)
    if errors:
        session["reservation_form"] = form_data
        session["reservation_errors"] = errors
        flash(next(iter(errors.values())), "error")
        return redirect(url_for("halls.hall_edit", hall_id=hall_id, open_form=1))

    create_reservation(hall, form_data)
    commit()
    flash("Rezervacija je uspješno dodana.", "success")
    return redirect(url_for("halls.hall_edit", hall_id=hall_id))


@bp.route("/halls/<int:hall_id>/delete", methods=["POST"])
def hall_delete(hall_id):
    hall = WeddingHall.get(id=hall_id)
    if hall is None:
        flash("Sala nije pronađena.", "error")
    elif hall.reservations.count() > 0:
        flash("Sala se ne moze obrisati jer ima povezane rezervacije.", "error")
    else:
        hall.delete()
        commit()
        flash("Sala je obrisana.", "success")
    return redirect(url_for("halls.halls_index"))