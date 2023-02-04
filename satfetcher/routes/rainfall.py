from flask import Blueprint, request

from ..satellite.processors import RainfallProcessor
from ..satellite.sources import OWSource
from ..validation import validate_request

blueprint = Blueprint('rainfall', __name__, url_prefix='/rainfall')

source = OWSource()
schema = {
    'lat': float,
    'lon': float
}

@blueprint.get('/')
def get():
    args = validate_request(request, schema)
    proc = RainfallProcessor(source, **args)
    return proc.process()
