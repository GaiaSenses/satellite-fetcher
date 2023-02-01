from flask import Blueprint, request, render_template

from .validation import validate_request
from .satellite import sources
from .satellite import processors

lightning = Blueprint('lightning', __name__, url_prefix='/lightning')
rainfall  = Blueprint('rainfall', __name__, url_prefix='/rainfall')
fire      = Blueprint('fire', __name__, url_prefix='/fire')

index = Blueprint('', __name__)

src = {
    'lightning': sources.GOESSource('GLM-L2-LCFA', maxcache=10),
    'rainfall': sources.OWSource(),
    'fire': sources.INPESource()
}

@lightning.get('/')
def get_lightning():
    args = validate_request(request, {'lat': float, 'lon': float})
    proc = processors.LightningProcessor(src['lightning'], **args)
    return proc.process()


@rainfall.get('/')
def get_rainfall():
    args = validate_request(request, {'lat': float, 'lon': float})
    proc = processors.RainfallProcessor(src['rainfall'], **args)
    return proc.process()


@fire.get('/')
def get_fire():
    args = validate_request(request, {'lat': float, 'lon': float})
    proc = processors.FireProcessor(src['fire'], **args)
    return proc.process()

@index.get('/')
def get_index():
    return render_template('index.html')
