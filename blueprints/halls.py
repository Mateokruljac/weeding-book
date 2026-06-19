from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from pony.orm import commit

from helpers import (
    create_reservation,
    get_hall_calendar_data,
    get_page,
    get_reservation_form,
    get_wedding_hall_map,
    to_float,
    validate_reservation,
    wedding_hall_exists,
)
from models import WeddingHall

bp = Blueprint("halls", __name__)

HALLS_PER_PAGE = 8


def hall_sort_key(hall, sort):
    if sort == "location":
        return hall.location
    if sort == "capacity":
        return hall.capacity
    if sort == "price":
        return hall.price
    return hall.name


def filter_halls(halls, search, location, min_val, max_val):
    result = halls

    if search:
        filtered = []
        for hall in result:
            if search in hall.name or search in hall.location:
                filtered.append(hall)
        result = filtered

    if location:
        filtered = []
        for hall in result:
            if location in hall.location:
                filtered.append(hall)
        result = filtered

    if min_val is not None:
        filtered = []
        for hall in result:
            if hall.price >= min_val:
                filtered.append(hall)
        result = filtered

    if max_val is not None:
        filtered = []
        for hall in result:
            if hall.price <= max_val:
                filtered.append(hall)
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

    if sort not in ("name", "location", "capacity", "price"):
        sort = "name"
    if order not in ("asc", "desc"):
        order = "asc"

    halls = list(WeddingHall.select())
    halls = filter_halls(halls, search, location, min_val, max_val)

    def sort_value(hall):
        return hall_sort_key(hall, sort)

    halls.sort(key=sort_value, reverse=(order == "desc"))
    halls, pagination = paginate_list(halls, page, HALLS_PER_PAGE)

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

    reservation_form = session.pop("reservation_form", None)
    reservation_errors = session.pop("reservation_errors", None)
    open_form = request.args.get("open_form") == "1" or bool(reservation_form)

    return render_template(
        "halls/form.html",
        hall=hall,
        open_form=open_form,
        reservation_form=reservation_form,
        reservation_errors=reservation_errors,
    )


@bp.route("/halls/<int:hall_id>/reservations")
def hall_reservations_json(hall_id):
    hall = WeddingHall.get(id=hall_id)
    if hall is None:
        return jsonify({"error": "Sala nije pronađena."}), 404

    def reservation_edit_url(reservation_id):
        return url_for("reservations.reservation_edit", reservation_id=reservation_id)

    data = get_hall_calendar_data(hall, reservation_edit_url)
    return jsonify(data)


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
        for error_message in errors.values():
            flash(error_message, "error")
            break
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
