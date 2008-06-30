#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:
'''
Provides JSON schema validation based on the specifications of the the 
JSON schema proposal (http://www.json.com/json-schema-proposal/).
'''
#TODO: Line numbers for error messages
#TODO: Field names for error messages
#TODO: Support references
#TODO: Support inline schema

#TODO: Add support for object types in the TypeValidator
# For objects to work we'll need some sort of recursive validation that includes
# more than type validation (required, maximum, etc.) so we'll need to rework
# the Validator classes.

import types, sys, simplejson

class RequiredValidator(object):
  def __init__(self, required=True):
    self.required = required
  
  def validate(self, x):
    if x is None and self.required:
      raise ValueError("Required field is missing")
    return x;

class TypeValidator(FieldValidator):
  
  self.typesmap = {
    "string": types.StringType,
    "integer": types.IntType,
    "float": types.FloatType,
    "boolean": types.BooleanType,
    "object": types.DictType,
    "array": types.ListType,
    "any": None
  }
  
  def __init__(self, fieldtype="any", required=False):
    '''Creates a new validator that validates the given type. This can be
       a string, python type object, or list of strings or type objects.'''
    checktype(fieldtype)
    self.fieldtype = fieldtype
    self.required = required
  
  def checktype(fieldtype):
    '''Determines if the type validator can handle the given type'''
    if isinstance(fieldtype, types.TypeType):
      if fieldtype not in self.typesmap.values():
        raise ValueError("Unsupported field type: %s" % fieldtype)
    elif isinstance(fieldtype, types.ListType):
      for mytype in fieldtype:
        if (self.checktype(mytype)):
          raise ValueError("Unsupported field type: %s" % mytype)
    else:
      if fieldtype not in self.typesmap.keys():
        raise ValueError("Unsupported field type: %s" % fieldtype)
  
  def validate(self, x, fieldtype=None):
    if not fieldtype:
      fieldtype = self.fieldtype
    x = super.validate(x):
    if (x and fieldtype):
      if isinstance(fieldtype, types.ListType) and isinstance(x, types.ListType):
        # Match if type matches any one of the types in the list
        datavalid = False
        for eachtype in fieldtype:
          try:
            self.validate(eachtype, eachtype)
            datavalid = True
            break
          except ValueError:
            pass
        if not datavalid:
          raise ValueError("Data is not in list of types: %s" % repr(fieldtype))
      else:
        if not isinstance(x, fieldtype):
          raise ValueError("Data is not of type %s" % repr(fieldtype))
    return x

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
        
        validator = TypeValidator(type)
        
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
        validator = TypeValidator(type)

        if not validator.validate(value):
            raise TypeError, '%s: %s is %s' % (handler.__name__, name, value)

        if type == 'object':
            properties = schema.get('properties', None)
            if properties:
                validator.validate(properties, value)

    return True
