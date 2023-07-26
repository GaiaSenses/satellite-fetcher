from flask import Blueprint, request

from ..satellite.processors import BrightnessTemperatureProcessor
from ..satellite.sources import GOESSource
from ..validation import validate_request

blueprint = Blueprint('brightness', __name__, url_prefix='/brightness')

source = GOESSource('ABI-L2-CMIPF', maxcache=10)
schema = {
    'lat': float,
    'lon': float,
}

@blueprint.get('/')
def get():
    args = validate_request(request, schema)
    proc = BrightnessTemperatureProcessor(source, **args)
    return proc.process()
