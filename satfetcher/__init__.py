from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from .routes import fire, lightning, rainfall, index
from . import errors


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    CORS(app)

    app.register_blueprint(index.blueprint)

    app.register_blueprint(lightning.blueprint)
    app.register_blueprint(rainfall.blueprint)
    app.register_blueprint(fire.blueprint)

    app.register_error_handler(
        errors.ValidationError, errors.handle_validation_error)

    return app
