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

class JSONValidator(object):
  
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
  
  def validate_optional(self, x, fieldname, fieldtype=None, optional=False):
    '''Validates that the given field is present if optional is false'''
    # Make sure the field is present
    if fieldname in x.keys() and not optional:
      raise ValueError("Required field %s is missing" % fieldname)
    return x
  
  def validate_nullable(self, x, fieldname, fieldtype=None, nullable=False):
    '''Validates that the given field is not null if the field is present and
       nullable is false'''
    if (fieldname in x.keys() and x.get(fieldname) is None and not nullable):
      raise ValueError("%s is not nullable.")
    return x
  
  def validate_unique(self, x, fieldname, fieldtype=None, unique=False):
    '''Validates that the given field is unique in the instance object tree'''
    # TODO: Support unique values
    # TODO: What does it mean to be unique in the object tree? If a child node
    #       is marked unique does that mean that parent nodes need to be checked
    #       for uniqueness?
    return x
  
  def validate_minimum(self, x, fieldname, fieldtype=types.IntType, minimum=None):
    '''Validates that the field is longer than or equal to the minimum length if
       specified'''
    # TODO: Support array field types.
    # TODO: Ignore non-array,non-number field types
    # TODO: What should be done if the type field is an array with number and
    #       non-number types? What about "any"?
    if (minimum is not None and x.get(fieldname) is not None):
      value = x.get(fieldname)
      if (value is not None and value < minimum):
        raise ValueError("%s is less than minimum value: %f" % fieldname, minimum)
    return x
  
  def validate_maximum(self, x, fieldname, fieldtype=types.IntType, maximum=None):
    '''Validates that the field is shorter than or equal to the maximum length
       if specified'''
    # TODO: Support array field types.
    # TODO: Ignore non-array,non-number field types
    # TODO: What should be done if the type field is an array with number and
    #       non-number types? What about "any"?
    if (maximum is not None and x.get(fieldname) is not None):
      value = x.get(fieldname)
      if (value is not None and value > maximum):
        raise ValueError("%s is greater than maximum value: %f" % fieldname, maximum)
    return x
  
  def validate_pattern(self, x, fieldname, fieldtype=None, pattern=None):
    '''Validates that the field is longer than the minimum length if specified'''
    # TODO: support regex patterns
    return x
  
  def validate_length(self, x, fieldname, fieldtype=types.StringType, length=None):
    '''Validates that the value of the given field is shorter than the specified
       length if a string'''
    if (length is not None and x.get(fieldname) is not None and len(x.get(fieldname) > length):
      raise ValueError("%s is greater than maximum value: %f" % fieldname, maximum)
    return x
  
  def validate_options(self, x, fieldname, fieldtype=types.StringType, options=None):
    '''Validates that the value of the field is equal to one of the specified
       option values if specified'''
    if (options is not None and x.get(fieldname) is not None):
      if (not isinstance(options, types.ListType)):
        raise ValueError("Options specification for field '%s' is not a list type", fieldname)
      if (x.get(fieldname) not in options):
        raise ValueError("Value of field '%s' is not in options specification: %s" % fieldname, repr(options))
    return x
  
  def validate_unconstrained(self, x, fieldname, fieldtype=types.StringType, unconstrained=None):
    return x
  
  def validate_readonly(self, x, fieldname, fieldtype=types.StringType, readonly=None):
    return x
  
  def validate_description(self, x, fieldname, fieldtype=types.StringType, description=None):
    return x
  
  def validate_format(self, x, fieldname, fieldtype=types.StringType, format=None):
    '''Validates that the value of the field matches the predifined format
       specified.'''
    # No definitions are currently defined for formats
    return x
  
  def validate_default(self, x, fieldname, fieldtype=types.StringType, default=None):
    return x
  
  def validate_transient(self, x, fieldname, fieldtype=types.StringType, transient=None):
    return x
  
  #fieldtype2 is required to give the same definition as other validator functions
  def validate_type(self, x, fieldname, fieldtype=None, fieldtype2=None):
    '''Validates that the fieldtype specified is correct for the given
       data'''
    # fieldtype and fieldtype2 should be the same but we will validate on
    # fieldtype2 for consistency
    
    #TODO: Support values from the 'Schema Definition' section of the proposal
    if (fieldtype2 is not None and x.get(fieldname) is not None):
      if isinstance(fieldtype2, types.ListType):
        # Match if type matches any one of the types in the list
        datavalid = False
        for eachtype in fieldtype2:
          try:
            self.validate_type(x, fieldname, eachtype, eachtype)
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
