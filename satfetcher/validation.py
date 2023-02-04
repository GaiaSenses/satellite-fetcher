from flask import Request

from .errors import ValidationError

def is_optional(x):
    try:
        return x['optional']
    except:
        return False

def conversion_fn(x):
    try:
        return x['type']
    except:
        return x

def validate_request(req: Request, schema: dict):
    error = {}
    res = {}

    for param, val in schema.items():
        if param not in req.args:
            if not is_optional(val):
                error[param] = 'missing value'
        else:
            arg = req.args.get(param, type=conversion_fn(val))

            if arg is None:
                error[param] = f'invalid value \'{req.args[param]}\''
            else:
                res[param] = arg

    if error:
        raise ValidationError(error)

    return res
