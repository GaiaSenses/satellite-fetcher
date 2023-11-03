from flask import Blueprint, request
from pydantic import ValidationError

from ..models.rainfall import RainfallQueryParams

from ..satellite.processors import RainfallProcessor
from ..satellite.sources import OWSource

blueprint = Blueprint('rainfall', __name__, url_prefix='/rainfall')

source = OWSource()

@blueprint.get('/')
def get():
    try:
        params = RainfallQueryParams(**request.args)
        proc = RainfallProcessor(source, **params.model_dump())
        return proc.process().model_dump(by_alias=True)
    except ValidationError as e:
        return e.json(include_url=False), 400
