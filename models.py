from pathlib import Path

from pony.orm import Database, PrimaryKey, Required, Set

db = Database()

STATUS_APPROVED = "approved"
STATUS_NOT_APPROVED = "not approved"


class WeddingHall(db.Entity):
    _table_ = "sale"
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    location = Required(str)
    capacity = Required(int)
    price = Required(float)
    reservations = Set("Reservation")


class Reservation(db.Entity):
    _table_ = "rezervacije"
    id = PrimaryKey(int, auto=True)
    wedding_hall = Required("WeddingHall", column="wedding_hall_id")
    bride_name = Required(str)
    groom_name = Required(str)
    bride_contact = Required(str)
    groom_contact = Required(str)
    date = Required(str)
    guest_count = Required(int)
    status = Required(str)
    price = Required(float)


def init_db():
    db_path = Path(__file__).parent / "wedding.db"
    db.bind(provider="sqlite", filename=str(db_path), create_db=True)
    db.generate_mapping(create_tables=True)

