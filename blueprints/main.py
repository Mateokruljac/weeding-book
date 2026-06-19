from datetime import date

from flask import Blueprint, render_template
from pony.orm import select

from models import Reservation, STATUS_APPROVED, WeddingHall

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    today = date.today().isoformat()

    total_halls = WeddingHall.select().count()
    total_reservations = Reservation.select().count()
    approved_reservations = select(
        r for r in Reservation
        if r.status == STATUS_APPROVED or r.status == "approved"
    ).count()
    not_approved_reservations = max(total_reservations - approved_reservations, 0)

    upcoming_reservations = (
        select(
            r for r in Reservation
            if (r.status == STATUS_APPROVED or r.status == "approved") and r.date >= today
        )
        .order_by(Reservation.date)[:5]
    )

    return render_template(
        "home.html",
        total_halls=total_halls,
        total_reservations=total_reservations,
        approved_reservations=approved_reservations,
        not_approved_reservations=not_approved_reservations,
        upcoming_reservations=upcoming_reservations,
    )
