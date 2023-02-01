from flask import Blueprint, request, render_template

import os

from .validation import validate_request
from .satellite import sources
from .satellite import processors

lightning = Blueprint('lightning', __name__, url_prefix='/lightning')
rainfall  = Blueprint('rainfall', __name__, url_prefix='/rainfall')
fire      = Blueprint('fire', __name__, url_prefix='/fire')

index = Blueprint('', __name__)

source_factory = sources.DataSourceFactory()

@lightning.get('/')
def get():
    args = validate_request(request, {'lat': float, 'lon': float})
    ds = source_factory.create('lightning')
    proc = processors.LightningProcessor(ds, **args)
    return proc.process()


@rainfall.get('/')
def get():
    args = validate_request(request, {'lat': float, 'lon': float})
    ds = source_factory.create('rainfall')
    proc = processors.RainfallProcessor(ds, **args)
    return proc.process()


@fire.get('/')
def get():
    args = validate_request(request, {'lat': float, 'lon': float})
    ds = source_factory.create('fire')
    proc = processors.FireProcessor(ds, **args)
    return proc.process()

@index.get('/')
def get():
    return render_template('index.html')
