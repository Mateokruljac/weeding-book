from datetime import date

from flask import Blueprint, render_template

from models import STATUS_APPROVED, Reservation, WeddingHall

bp = Blueprint("main", __name__)


def reservation_date(reservation):
    return reservation.date


@bp.route("/")
def index():
    today = date.today().isoformat()

    total_halls = WeddingHall.select().count()
    all_reservations = list(Reservation.select())
    approved = [r for r in all_reservations if r.status == STATUS_APPROVED]

    total_reservations = len(all_reservations)
    approved_reservations = len(approved)
    not_approved_reservations = total_reservations - approved_reservations

    upcoming = [r for r in approved if r.date >= today]
    upcoming.sort(key=reservation_date)
    upcoming_reservations = upcoming[:5]

    return render_template(
        "home.html",
        total_halls=total_halls,
        total_reservations=total_reservations,
        approved_reservations=approved_reservations,
        not_approved_reservations=not_approved_reservations,
        upcoming_reservations=upcoming_reservations,
    )
