from django.utils import simplejson
import types, sys

def string_handler(x):
    return isinstance(x, types.StringTypes)

def number_handler(x):
    return isinstance(x, types.FloatType)

def integer_handler(x):
    return isinstance(x, types.IntType)

def boolean_handler(x):
    return isinstance(x, types.BooleanType)

def object_handler(x):
    return isinstance(x, types.DictType)

def array_handler(x):
    return isinstance(x, types.ListType)

def null_handler(x):
    return isinstance(x, types.NoneType)

def integer_handler(x):
    return isinstance(x, types.IntType)

def any_handler(x):
    return True

valid_types = ['string', 'number', 'integer', 'boolean', 'object', 'array', 'null', 'any']
handlers = {}
for type in valid_types:
    handlers[type] = locals()['%s_handler' % type]

def schema_validate(schema):
    '''
    >>> schema_validate({"name": {"type": "string"}})
    True
    >>> schema_validate({"spam": {"type": "object"}})
    True
    >>> schema_validate({"spam": {"type": "object", "properties": {"count": {"type": "integer"}}}})
    True
    >>> schema_validate({"php": {"foo": ["bar", "baz"]}})
    Traceback (most recent call last):
    ...
    KeyError: 'type'
    >>> schema_validate({"php": {"type": "bar"}})
    Traceback (most recent call last):
    ...
    KeyError: 'bar'
    '''

    for name in schema:
        type = schema[name]['type']

        if type not in valid_types:
            raise KeyError, type

        if type == 'object':
            properties = schema.get('properties', None)
            if properties:
                schema_validate(properties)

    return True

def validate(schema, json):
    '''
    >>> schema = {"name": {"type": "string"}, "age": {"type": "integer"}, "job": {"type": "object", "properties": {"name": {"type": "string"}}}}
    >>> validate(schema, {"name": "hoge", "age": 1, "job": {"name": "sarary"}})
    True
    >>> validate(schema, {})
    Traceback (most recent call last)
    ...
    TypeError: object_handler: "job" is None
    '''

    for name in schema:
        type = schema[name]['type']
        value = json.get(name, None)
        handler = handlers[type]

        if not handler(value):
            raise TypeError, '%s: %s is %s' % (handler.__name__, name, value)

        if type == 'object':
            properties = schema.get('properties', None)
            if properties:
                validate(properties, value)

    return True

from google.appengine.ext import webapp
class JsonValidateHandler(webapp.RequestHandler):

    def post(self):
        try:
            json = simplejson.loads(self.request.POST['json'])
            schema = simplejson.loads(self.request.POST['schema'])
            schema_validate(schema)
            validate(schema, json)
            self.response.headers['content-type'] = 'application/json'
            self.response.out.write(simplejson.dumps(json))
        except:
            self.response.headers['content-type'] = 'text/plain'
            self.response.out.write(sys.exc_info()[1])

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
