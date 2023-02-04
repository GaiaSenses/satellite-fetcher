from flask import Blueprint, request

from ..satellite.processors import LightningProcessor
from ..satellite.sources import GOESSource
from ..validation import validate_request

blueprint = Blueprint('lightning', __name__, url_prefix='/lightning')

source = GOESSource('GLM-L2-LCFA', maxcache=10)
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
    proc = LightningProcessor(source, **args)
    return proc.process()
