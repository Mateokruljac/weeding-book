from datetime import date

from flask import Flask
from pony.flask import Pony

from blueprints.analytics import bp as analytics_bp
from blueprints.halls import bp as halls_bp
from blueprints.main import bp as main_bp
from blueprints.reservations import bp as reservations_bp
from config import Config
from models import STATUS_APPROVED, STATUS_NOT_APPROVED, init_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_db()
    Pony(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(halls_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(analytics_bp)

    @app.context_processor
    def inject_globals():
        return {"today": date.today().isoformat()}

    @app.template_filter("status_label")
    def status_label(status):
        if status == "approved":
            return "Odobrena"
        if status == "not_approved":
            return "Nije odobrena"
        if status == STATUS_APPROVED:
            return "Odobrena"
        if status == STATUS_NOT_APPROVED:
            return "Nije odobrena"
        return status

    return app