from functools import partial
import json

import colander
from daybed.schemas import DefinitionValidator, SchemaValidator


def validator(request, schema):
    """Validates the request according to the given schema"""
    try:
        body = request.body
        dictbody = json.loads(body) if body else {}
        validate_against_schema(request, schema, dictbody)
    except ValueError, e:
        request.errors.add('body', 'body', str(e))


#  Validates a request body according model definition schema.
definition_validator = partial(validator, schema=DefinitionValidator())


def schema_validator(request):
    """Validates a request body according to its model definition.
    """
    model_id = request.matchdict['model_id']

    doc = request.db.get_model_definition(model_id)
    if doc:
        schema = SchemaValidator(doc['definition'])
        validator(request, schema)
    else:
        request.errors.add('path', 'modelname',
                           'Unknown model %s' % model_id)
        request.errors.status = 404


def validate_against_schema(request, schema, data):
    try:
        request.data_clean = schema.deserialize(data)
    except colander.Invalid, e:
        for error in e.children:
            # here we transform the errors we got from colander into cornice
            # errors
            for field, error in error.asdict().items():
                request.errors.add('body', field, error)
