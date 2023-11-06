from flask import Blueprint, request
from pydantic import ValidationError

from .model import LightningQueryParams
from .processor import LightningProcessor

from ..sources import GOESSource

blueprint = Blueprint('lightning', __name__, url_prefix='/lightning')

source = GOESSource('GLM-L2-LCFA', maxcache=10)

@blueprint.get('/')
def get():
    try:
        params = LightningQueryParams(**request.args)
        proc = LightningProcessor(source, **params.model_dump())
        return proc.process().model_dump(by_alias=True)
    except ValidationError as e:
        return e.json(include_url=False), 400
