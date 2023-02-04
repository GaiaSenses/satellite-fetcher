from flask import Blueprint, request

from ..satellite.processors import FireProcessor
from ..satellite.sources import INPESource
from ..validation import validate_request

blueprint = Blueprint('fire', __name__, url_prefix='/fire')

source = INPESource()
schema = {
    'lat': float,
    'lon': float,
    'dist': {
        'type': float,
        'optional': True
    }
}

@blueprint.get('/')
def get():
    args = validate_request(request, schema)
    proc = FireProcessor(source, **args)
    return proc.process()
