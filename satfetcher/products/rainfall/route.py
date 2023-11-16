from flask import Blueprint, current_app, request
from pydantic import ValidationError

from .model import RainfallQueryParams
from .processor import RainfallProcessor

from ..sources import OWSource

blueprint = Blueprint('rainfall', __name__, url_prefix='/rainfall')

source = OWSource()

@blueprint.get('/')
def get():
    params = RainfallQueryParams(**request.args)
    proc = RainfallProcessor(source, **params.model_dump())
    return proc.process().model_dump(by_alias=True, exclude_none=True)
