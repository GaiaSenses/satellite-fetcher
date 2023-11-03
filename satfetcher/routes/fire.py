from flask import Blueprint, request
from pydantic import ValidationError

from ..models.fire import FireQueryParams

from ..satellite.processors import FireProcessor
from ..satellite.sources import FIRMSSource

blueprint = Blueprint('fire', __name__, url_prefix='/fire')

source = FIRMSSource()

@blueprint.get('/')
def get():
    try:
        params = FireQueryParams(**request.args)
        proc = FireProcessor(source, **params.model_dump())
        return proc.process().model_dump(by_alias=True)
    except ValidationError as e:
        return e.json(include_url=False), 400
