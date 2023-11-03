from flask import Blueprint, request
from pydantic import ValidationError

from ..models.brightness import BrightnessQueryParams

from ..satellite.processors import BrightnessTemperatureProcessor
from ..satellite.sources import GOESSource

blueprint = Blueprint('brightness', __name__, url_prefix='/brightness')

source = GOESSource('ABI-L2-CMIPF', maxcache=10)

@blueprint.get('/')
def get():
    try:
        params = BrightnessQueryParams(**request.args)
        proc = BrightnessTemperatureProcessor(source, **params.model_dump())
        return proc.process().model_dump(by_alias=True)
    except ValidationError as e:
        return e.json(include_url=False), 400
