from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flaskr.configuration.config import Config


db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    db.init_app(app)

    from flaskr.main.routes import main
    app.register_blueprint(main)
    from flaskr.configuration.routes import config
    app.register_blueprint(config)
    from flaskr.users.routes import user
    app.register_blueprint(user)

    with app.app_context():
        db.create_all()
        try:
            db.session.commit()
        except IntegrityError:
            pass
    return app


