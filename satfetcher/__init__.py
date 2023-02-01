from flask import Flask

from . import routes
from . import errors


def create_app():
    app = Flask(__name__)

    app.register_blueprint(routes.index)

    app.register_blueprint(routes.lightning)
    app.register_blueprint(routes.rainfall)
    app.register_blueprint(routes.fire)

    app.register_error_handler(
        errors.ValidationError, errors.handle_validation_error)

    return app
