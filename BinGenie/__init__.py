from flask import Flask, render_template
from .config import DevelopmentConfig
from flask_migrate import Migrate
from .database import db
#db = SQLAlchemy()

def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DevelopmentConfig)
    db.init_app(app)
    Migrate(app, db)
    with app.app_context():
        db.create_all()
    from .bins import bins_bp
    from .item import items_bp
    from .locations import locations_bp
    from .home import home_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(bins_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(locations_bp)

    return app
