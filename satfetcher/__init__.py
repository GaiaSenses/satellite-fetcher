from flask import Flask
from flask_cors import CORS
from pydantic import ValidationError
from werkzeug.middleware.proxy_fix import ProxyFix
import os

from satfetcher.errors import InvalidLocation

from .products.rainfall import route as rainfall
from .products.lightning import route as lightning
from .products.fire import route as fire
from .products.brightness import route as brightness

from . import index

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
CORS(app)

if os.getenv('PROFILE') is not None:
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir='profile')

app.register_blueprint(index.blueprint)
app.register_blueprint(lightning.blueprint)
app.register_blueprint(rainfall.blueprint)
app.register_blueprint(fire.blueprint)
app.register_blueprint(brightness.blueprint)


@app.errorhandler(InvalidLocation)
def handle_invalid_location(e: InvalidLocation):
    msg = f'invalid location [{e.lat}, {e.lon}]'
    app.logger.error(msg, exc_info=True)
    return {'msg': msg }, 400

@app.errorhandler(ValidationError)
def handle_validation_error(e: ValidationError):
    res = {
        'msg': 'validation error',
    }
    app.logger.error(e.json(indent=2), exc_info=True)
    return res, 400
