#!/usr/bin/env python
#:coding=utf-8:
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
#TODO: Add checks to make sure the schema itself is valid

import types, sys, simplejson

# TODO: Create a map of validation functions like Muraoka Yusuke (村岡友介)
#       created in the original implementation. However, the functions need
#       to be pulled from the JSONValidator class namespace rather than
#       the local namespace.

# ALTERNATIVE: Go back to the class based approach and create validators
#              but make the type validator a special validator that
#              recursively processes the object definitions.

# ALTERNATIVE: Same as the class based approach but type validator only 
#              validates the object is an object if it's specified as an
#              object type. Another driver class would perform the recursive
#              processing.

# TODO: Test support for unicode string types
typesmap = {
  "string": types.StringType,
  "integer": types.IntType,
  "float": types.FloatType,
  "boolean": types.BooleanType,
  "object": types.DictType,
  "array": types.ListType,
  "any": None
}

schemadefault = {
  "optional": False,
  "nullable": False,
  "unique": False,
  "minimum": None,
  "maximum": None,
  "pattern": None,
  "length": None,
  "options": None,
  "unconstrained": None,
  "readonly": None,
  "description": None,
  "format": None,
  "default": None,
  "transient": None,
  "type": None
}

def checktype(fieldtype):
  '''Determines if the type validator can handle the given type'''
  if isinstance(fieldtype, types.TypeType):
    if fieldtype not in typesmap.values():
      raise ValueError("Unsupported field type: %s" % fieldtype)
  elif isinstance(fieldtype, types.ListType):
    for mytype in fieldtype:
      if checktype(mytype):
        raise ValueError("Unsupported field type: %s" % mytype)
  else:
    if fieldtype not in typesmap.keys():
      raise ValueError("Unsupported field type: %s" % fieldtype)

def validate_optional(x, fieldname, fieldtype=None, optional=False):
  '''Validates that the given field is present if optional is false'''
  # Make sure the field is present
  if fieldname not in x.keys() and not optional:
    raise ValueError("Required field %s is missing" % fieldname)
  return x

def validate_nullable(x, fieldname, fieldtype=None, nullable=False):
  '''Validates that the given field is not null if the field is present and
     nullable is false'''
  if fieldname in x.keys() and x.get(fieldname) is None and not nullable:
    raise ValueError("%s is not nullable." % fieldname)
  return x

def validate_unique(x, fieldname, fieldtype=None, unique=False):
  '''Validates that the given field is unique in the instance object tree'''
  # TODO: Support unique values
  # TODO: What does it mean to be unique in the object tree? If a child node
  #       is marked unique does that mean that parent nodes need to be checked
  #       for uniqueness?
  return x

def validate_minimum(x, fieldname, fieldtype=types.IntType, minimum=None):
  '''Validates that the field is longer than or equal to the minimum length if
     specified'''
  if minimum is not None and x.get(fieldname) is not None:
    value = x.get(fieldname)
    if value is not None:
      if (isinstance(value, types.IntType) or isinstance(value,types.FloatType)) and value < minimum:
        raise ValueError("%s is less than minimum value: %f" % (value, minimum))
      elif isinstance(value,types.ListType) and len(value) < minimum:
        raise ValueError("%s has fewer values than the minimum: %f" % (value, minimum))
  return x

def validate_maximum(x, fieldname, fieldtype=types.IntType, maximum=None):
  '''Validates that the field is shorter than or equal to the maximum length
     if specified'''
  if maximum is not None and x.get(fieldname) is not None:
    value = x.get(fieldname)
    if value is not None:
      if (isinstance(value, types.IntType) or isinstance(value,types.FloatType)) and value > maximum:
        raise ValueError("%s is greater than maximum value: %f" % (value, maximum))
      elif isinstance(value,types.ListType) and len(value) > maximum:
        raise ValueError("%s has more values than the maximum: %f" % (value, maximum))
  return x

def validate_pattern(x, fieldname, fieldtype=None, pattern=None):
  '''Validates that the field is longer than the minimum length if specified'''
  # TODO: support regex patterns
  return x

def validate_length(x, fieldname, fieldtype=None, length=None):
  '''Validates that the value of the given field is shorter than the specified
     length if a string'''
  value = x.get(fieldname)
  if length is not None and \
     value is not None and \
     isinstance(value, types.StringType) and \
     len(value) > length:
    raise ValueError("%s is greater than maximum value: %f" % (value, length))
  return x

def validate_options(x, fieldname, fieldtype=None, options=None):
  '''Validates that the value of the field is equal to one of the specified
     option values if specified'''
  value = x.get(fieldname)
  if options is not None and value is not None:
    if not isinstance(options, types.ListType):
      raise ValueError("Options specification for field '%s' is not a list type", fieldname)
    if value not in options:
      raise ValueError("Value %s is not in options specification: %s" % value, repr(options))
  return x

def validate_unconstrained(x, fieldname, fieldtype=None, unconstrained=None):
  return x

def validate_readonly(x, fieldname, fieldtype=None, readonly=None):
  return x

def validate_description(x, fieldname, fieldtype=None, description=None):
  return x

def validate_format(x, fieldname, fieldtype=types.StringType, format=None):
  '''Validates that the value of the field matches the predifined format
     specified.'''
  # No definitions are currently defined for formats
  return x

def validate_default(x, fieldname, fieldtype=types.StringType, default=None):
  return x

def validate_transient(x, fieldname, fieldtype=types.StringType, transient=None):
  return x

#fieldtype2 is required to give the same definition as other validator functions
def validate_type(x, fieldname, fieldtype=None, fieldtype2=None):
  '''Validates that the fieldtype specified is correct for the given
     data'''
  # fieldtype and fieldtype2 should be the same but we will validate on
  # fieldtype2 for consistency
  converted_fieldtype = convert_type(fieldtype2)
  value = x.get(fieldname)
  
  #TODO: Support values from the 'Schema Definition' section of the proposal
  if converted_fieldtype is not None and x.get(fieldname) is not None:
    if isinstance(converted_fieldtype, types.ListType):
      # Match if type matches any one of the types in the list
      datavalid = False
      for eachtype in converted_fieldtype:
        try:
          validate_type(x, fieldname, eachtype, eachtype)
          datavalid = True
          break
        except ValueError:
          pass
      if not datavalid:
        raise ValueError("Value %s is not in list of types: %s" % (value, repr(converted_fieldtype)))
    else:
      if not isinstance(value, converted_fieldtype):
        raise ValueError("Value %s is not of type %s" % (value, repr(converted_fieldtype)))
  return x
  
def convert_type(fieldtype):
  if isinstance(fieldtype, types.TypeType):
    return fieldtype
  elif isinstance(fieldtype, types.ListType):
    converted_fields = []
    for subfieldtype in fieldtype:
      converted_fields.append(convert_type(subfieldtype))
    return converted_fields
  elif fieldtype is None:
    return None
  else:
    fieldtype = str(fieldtype)
    if fieldtype in typesmap.keys():
      return typesmap[fieldtype]
    else:
      raise ValueError("Field type %s is not supported." % fieldtype)

def validate(data, schema):
  if isinstance(data, types.DictType):
    pass
  else:
    # Wrap the data in a dictionary
    datadict = {"_data": data }
    
    #Initialize defaults
    for schemaprop in schemadefault.keys():
      if schemaprop not in schema:
        schema[schemaprop] = schemadefault[schemaprop]
    
    for schemaprop in schema:
      # print schemaprop
      validatorname = "validate_"+schemaprop
      if validatorname in globals():
        validator = globals()[validatorname]
        validator(datadict,"_data", schema.get("type"), schema.get(schemaprop))
      else:
        raise ValueError("Schema property %s is not supported" % schemaprop)

if __name__ == '__main__':
  x = {"test": "test", "test2": 25, "test3": True, "test4": {"subtest": "test"}}
  validate_type(x, "test", "string","string")
  validate_type(x, "test2", "integer", "integer")
  validate_type(x, "test3", "boolean", "boolean")
  try:
    validate_type(x, "test4", "string", "string")
  except ValueError, e:
    pass