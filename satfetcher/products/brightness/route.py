from flask import Blueprint, request
from pydantic import ValidationError

from .model import BrightnessQueryParams
from .processor import BrightnessTemperatureProcessor

from ..sources import GOESSource

blueprint = Blueprint('brightness', __name__, url_prefix='/brightness')

source = GOESSource('ABI-L2-CMIPF')

@blueprint.get('/')
def get():
    params = BrightnessQueryParams(**request.args)
    proc = BrightnessTemperatureProcessor(source, **params.model_dump())
    return proc.process().model_dump(by_alias=True)
