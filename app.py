import sqlite3
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"
app.config["DATABASE"] = Path(app.root_path) / "wedding.db"


def get_db():
    if "db" not in g:
        db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g.db = db
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS sale (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL,
            lokacija TEXT NOT NULL,
            kapacitet INTEGER NOT NULL CHECK (kapacitet >= 0),
            cijena REAL NOT NULL CHECK (cijena >= 0)
        );

        CREATE TABLE IF NOT EXISTS rezervacije (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sala_id INTEGER NOT NULL,
            ime_i_prezime_mladenke TEXT NOT NULL,
            ime_i_prezime_mladozenje TEXT NOT NULL,
            kontakt_mladenka TEXT NOT NULL,
            kontakt_mladozenja TEXT NOT NULL,
            datum TEXT NOT NULL,
            broj_gostiju INTEGER NOT NULL CHECK (broj_gostiju > 0),
            status TEXT NOT NULL CHECK (status IN ('odobrena', 'nije odobrena')),
            cijena_najma REAL NOT NULL CHECK (cijena_najma >= 0),
            FOREIGN KEY (sala_id) REFERENCES sale (id) ON DELETE RESTRICT
        );
        """
    )
    db.commit()


@app.before_request
def ensure_database():
    init_db()


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/sale")
def sale_index():
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "naziv")
    order = request.args.get("order", "asc")
    page_raw = request.args.get("page", "1").strip()
    lokacija = request.args.get("lokacija", "").strip()
    min_cijena = request.args.get("min_cijena", "").strip()
    max_cijena = request.args.get("max_cijena", "").strip()

    allowed_sort = {"naziv", "lokacija", "kapacitet", "cijena"}
    if sort not in allowed_sort:
        sort = "naziv"
    if order not in {"asc", "desc"}:
        order = "asc"
    try:
        page = max(1, int(page_raw))
    except (TypeError, ValueError):
        page = 1

    per_page = 10

    conditions = []
    params = []

    if search:
        conditions.append("(naziv LIKE ? OR lokacija LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if lokacija:
        conditions.append("lokacija LIKE ?")
        params.append(f"%{lokacija}%")
    if min_cijena:
        try:
            parsed_min = float(min_cijena)
            conditions.append("cijena >= ?")
            params.append(parsed_min)
        except ValueError:
            pass
    if max_cijena:
        try:
            parsed_max = float(max_cijena)
            conditions.append("cijena <= ?")
            params.append(parsed_max)
        except ValueError:
            pass

    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    db = get_db()
    total_items = db.execute(
        f"SELECT COUNT(*) FROM sale {where_sql}", params
    ).fetchone()[0]
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * per_page

    query = (
        f"SELECT * FROM sale {where_sql} ORDER BY {sort} {order.upper()} "
        "LIMIT ? OFFSET ?"
    )
    sale = db.execute(query, [*params, per_page, offset]).fetchall()

    return render_template(
        "sale/index.html",
        sale=sale,
        search=search,
        filters={
            "lokacija": lokacija,
            "min_cijena": min_cijena,
            "max_cijena": max_cijena,
        },
        sorting={
            "sort": sort,
            "order": order,
        },
        pagination={
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items,
        },
    )


@app.route("/sale/create", methods=["GET", "POST"])
def sale_create():
    if request.method == "POST":
        naziv = request.form["naziv"].strip()
        lokacija = request.form["lokacija"].strip()
        kapacitet = request.form["kapacitet"].strip()
        cijena = request.form["cijena"].strip()

        if not naziv or not lokacija or not kapacitet or not cijena:
            flash("Sva polja za salu su obavezna.", "error")
        else:
            get_db().execute(
                """
                INSERT INTO sale (naziv, lokacija, kapacitet, cijena)
                VALUES (?, ?, ?, ?)
                """,
                (naziv, lokacija, int(kapacitet), float(cijena)),
            )
            get_db().commit()
            flash("Sala je uspjesno dodana.", "success")
            return redirect(url_for("sale_index"))

    return render_template("sale/form.html", sala=None)


def get_sala_by_id(sala_id):
    return get_db().execute("SELECT * FROM sale WHERE id = ?", (sala_id,)).fetchone()


def get_rezervacije_for_sala(sala_id):
    return get_db().execute(
        """
        SELECT id, ime_i_prezime_mladenke, ime_i_prezime_mladozenje, datum, status, broj_gostiju, cijena_najma
        FROM rezervacije
        WHERE sala_id = ?
        ORDER BY datum DESC
        """,
        (sala_id,),
    ).fetchall()


@app.route("/sale/<int:sala_id>/edit", methods=["GET", "POST"])
def sale_edit(sala_id):
    sala = get_sala_by_id(sala_id)
    if sala is None:
        flash("Sala nije pronadena.", "error")
        return redirect(url_for("sale_index"))

    if request.method == "POST":
        get_db().execute(
            """
            UPDATE sale
            SET naziv = ?, lokacija = ?, kapacitet = ?, cijena = ?
            WHERE id = ?
            """,
            (
                request.form["naziv"].strip(),
                request.form["lokacija"].strip(),
                int(request.form["kapacitet"]),
                float(request.form["cijena"]),
                sala_id,
            ),
        )
        get_db().commit()
        flash("Sala je uspjesno azurirana.", "success")
        return redirect(url_for("sale_index"))

    return render_template(
        "sale/form.html",
        sala=sala,
        rezervacije=get_rezervacije_for_sala(sala_id),
    )


@app.route("/sale/<int:sala_id>/delete", methods=["POST"])
def sale_delete(sala_id):
    try:
        get_db().execute("DELETE FROM sale WHERE id = ?", (sala_id,))
        get_db().commit()
        flash("Sala je obrisana.", "success")
    except sqlite3.IntegrityError:
        flash("Sala se ne moze obrisati jer ima povezane rezervacije.", "error")
    return redirect(url_for("sale_index"))


@app.route("/rezervacije")
def rezervacije_index():
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "datum")
    order = request.args.get("order", "asc")
    page_raw = request.args.get("page", "1").strip()
    status = request.args.get("status", "").strip()
    datum_od = request.args.get("datum_od", "").strip()
    datum_do = request.args.get("datum_do", "").strip()

    allowed_sort = {"datum", "cijena_najma", "broj_gostiju", "status"}
    if sort not in allowed_sort:
        sort = "datum"
    if order not in {"asc", "desc"}:
        order = "asc"
    try:
        page = max(1, int(page_raw))
    except (TypeError, ValueError):
        page = 1
    per_page = 10

    conditions = []
    params = []

    if search:
        conditions.append(
            """
            (
                r.ime_i_prezime_mladenke LIKE ?
                OR r.ime_i_prezime_mladozenje LIKE ?
                OR s.naziv LIKE ?
                OR s.lokacija LIKE ?
            )
            """
        )
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
    if status in {"odobrena", "nije odobrena"}:
        conditions.append("r.status = ?")
        params.append(status)
    if datum_od:
        conditions.append("r.datum >= ?")
        params.append(datum_od)
    if datum_do:
        conditions.append("r.datum <= ?")
        params.append(datum_do)

    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    db = get_db()
    total_items = db.execute(
        f"""
        SELECT COUNT(*)
        FROM rezervacije r
        JOIN sale s ON s.id = r.sala_id
        {where_sql}
        """,
        params,
    ).fetchone()[0]
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * per_page

    rezervacije = db.execute(
        f"""
        SELECT r.*, s.naziv AS sala_naziv, s.lokacija AS sala_lokacija
        FROM rezervacije r
        JOIN sale s ON s.id = r.sala_id
        {where_sql}
        ORDER BY r.{sort} {order.upper()}
        LIMIT ? OFFSET ?
        """,
        [*params, per_page, offset],
    ).fetchall()

    return render_template(
        "rezervacije/index.html",
        rezervacije=rezervacije,
        search=search,
        filters={
            "status": status,
            "datum_od": datum_od,
            "datum_do": datum_do,
        },
        sorting={
            "sort": sort,
            "order": order,
        },
        pagination={
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items,
        },
    )


def _available_sale():
    return get_db().execute("SELECT * FROM sale ORDER BY naziv ASC").fetchall()


@app.route("/rezervacije/create", methods=["GET", "POST"])
def rezervacije_create():
    sale = _available_sale()
    if request.method == "POST":
        data = (
            int(request.form["sala_id"]),
            request.form["ime_i_prezime_mladenke"].strip(),
            request.form["ime_i_prezime_mladozenje"].strip(),
            request.form["kontakt_mladenka"].strip(),
            request.form["kontakt_mladozenja"].strip(),
            request.form["datum"],
            int(request.form["broj_gostiju"]),
            request.form["status"],
            float(request.form["cijena_najma"]),
        )
        get_db().execute(
            """
            INSERT INTO rezervacije (
                sala_id, ime_i_prezime_mladenke, ime_i_prezime_mladozenje,
                kontakt_mladenka, kontakt_mladozenja, datum,
                broj_gostiju, status, cijena_najma
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            data,
        )
        get_db().commit()
        flash("Rezervacija je uspjesno dodana.", "success")
        return redirect(url_for("rezervacije_index"))

    return render_template("rezervacije/form.html", rezervacija=None, sale=sale)


def get_rezervacija_by_id(rezervacija_id):
    return get_db().execute(
        "SELECT * FROM rezervacije WHERE id = ?", (rezervacija_id,)
    ).fetchone()


@app.route("/rezervacije/<int:rezervacija_id>/edit", methods=["GET", "POST"])
def rezervacije_edit(rezervacija_id: int):
    rezervacija = get_rezervacija_by_id(rezervacija_id)
    if rezervacija is None:
        flash("Rezervacija nije pronadena.", "error")
        return redirect(url_for("rezervacije_index"))

    if request.method == "POST":
        get_db().execute(
            """
            UPDATE rezervacije
            SET sala_id = ?, ime_i_prezime_mladenke = ?, ime_i_prezime_mladozenje = ?,
                kontakt_mladenka = ?, kontakt_mladozenja = ?, datum = ?,
                broj_gostiju = ?, status = ?, cijena_najma = ?
            WHERE id = ?
            """,
            (
                int(request.form["sala_id"]),
                request.form["ime_i_prezime_mladenke"].strip(),
                request.form["ime_i_prezime_mladozenje"].strip(),
                request.form["kontakt_mladenka"].strip(),
                request.form["kontakt_mladozenja"].strip(),
                request.form["datum"],
                int(request.form["broj_gostiju"]),
                request.form["status"],
                float(request.form["cijena_najma"]),
                rezervacija_id,
            ),
        )
        get_db().commit()
        flash("Rezervacija je uspjesno azurirana.", "success")
        return redirect(url_for("rezervacije_index"))

    return render_template(
        "rezervacije/form.html",
        rezervacija=rezervacija,
        sale=_available_sale(),
    )


@app.route("/rezervacije/<int:rezervacija_id>/delete", methods=["POST"])
def rezervacije_delete(rezervacija_id: int):
    get_db().execute("DELETE FROM rezervacije WHERE id = ?", (rezervacija_id,))
    get_db().commit()
    flash("Rezervacija je obrisana.", "success")
    return redirect(url_for("rezervacije_index"))


@app.route("/analitika")
def analitika():
    db = get_db()
    ukupno = db.execute("SELECT COUNT(*) FROM rezervacije").fetchone()[0]
    odobrene = db.execute(
        "SELECT COUNT(*) FROM rezervacije WHERE status = 'odobrena'"
    ).fetchone()[0]
    neodobrene = db.execute(
        "SELECT COUNT(*) FROM rezervacije WHERE status = 'nije odobrena'"
    ).fetchone()[0]
    ukupan_prihod = db.execute(
        "SELECT COALESCE(SUM(cijena_najma), 0) FROM rezervacije WHERE status = 'odobrena'"
    ).fetchone()[0]
    prosjecna_cijena = db.execute(
        "SELECT COALESCE(AVG(cijena_najma), 0) FROM rezervacije"
    ).fetchone()[0]

    top_sale = db.execute(
        """
        SELECT s.naziv, COUNT(r.id) AS broj
        FROM rezervacije r
        JOIN sale s ON s.id = r.sala_id
        GROUP BY s.id, s.naziv
        ORDER BY broj DESC
        LIMIT 6
        """
    ).fetchall()

    by_month = db.execute(
        """
        SELECT SUBSTR(datum, 1, 7) AS mjesec, COUNT(*) AS broj
        FROM rezervacije
        GROUP BY mjesec
        ORDER BY mjesec ASC
        """
    ).fetchall()

    return render_template(
        "analitika.html",
        stats={
            "ukupno": ukupno,
            "odobrene": odobrene,
            "neodobrene": neodobrene,
            "ukupan_prihod": ukupan_prihod,
            "prosjecna_cijena": prosjecna_cijena,
        },
        top_sale=top_sale,
        by_month=by_month,
    )


if __name__ == "__main__":
    app.run()
