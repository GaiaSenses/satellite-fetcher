from flask import Request

from .errors import ValidationError


def validate_request(req: Request, schema: dict):
    error = {}
    res = {}

    for param, tp in schema.items():
        if param not in req.args:
            error[param] = 'missing value'
        else:
            val = req.args.get(param, type=tp)
            if not val:
                error[param] = 'invalid value'
            else:
                res[param] = val

    if error:
        raise ValidationError(error)

    return res
