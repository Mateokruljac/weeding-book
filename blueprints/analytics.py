from datetime import date

from flask import Blueprint, render_template

from models import STATUS_APPROVED, Reservation, WeddingHall

bp = Blueprint("analytics", __name__)


@bp.route("/analytics")
def analytics():
    today = date.today().isoformat()

    all_reservations = list(Reservation.select())
    approved = [r for r in all_reservations if r.status == STATUS_APPROVED]

    total = len(all_reservations)
    approved_count = len(approved)
    not_approved = total - approved_count

    total_halls = WeddingHall.select().count()
    approval_rate = round(approved_count / total * 100, 1) if total else 0
    total_revenue = sum(r.price for r in approved)
    avg_guests = round(sum(r.guest_count for r in approved) / approved_count) if approved_count else 0
    upcoming = sum(1 for r in approved if r.date >= today)

    top_halls = []
    for hall in WeddingHall.select():
        count = sum(1 for r in approved if r.wedding_hall == hall)
        top_halls.append({"name": hall.name, "count": count})
    top_halls.sort(key=lambda h: h["count"], reverse=True)
    top_halls = top_halls[:6]

    by_month_dict = {}
    for r in approved:
        month = r.date[:7]
        if month not in by_month_dict:
            by_month_dict[month] = {"month": month, "count": 0, "revenue": 0}
        by_month_dict[month]["count"] += 1
        by_month_dict[month]["revenue"] += r.price

    by_month = sorted(by_month_dict.values(), key=lambda m: m["month"])
    for m in by_month:
        m["revenue"] = round(m["revenue"], 2)

    return render_template(
        "analytics.html",
        stats={
            "total": total,
            "approved": approved_count,
            "not_approved": not_approved,
            "total_halls": total_halls,
            "approval_rate": approval_rate,
            "total_revenue": total_revenue,
            "avg_guests": avg_guests,
            "upcoming": upcoming,
        },
        top_halls=top_halls,
        by_month=by_month,
    )
