#!/usr/bin/env python
#:coding=utf-8:
#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:

'''
Provides JSON schema validation based on the specifications of the the 
JSON schema proposal (http://www.json.com/json-schema-proposal/).
'''

#TODO: Line numbers for error messages
#TODO: Support references
#TODO: Support inline schema
#TODO: Add checks to make sure the schema itself is valid
#TODO: Support adding default values to the original json document if they
#      aren't present.

#TODO: Support command line validation kind of like how simplejson allows 
#      encoding using the "python -m<modulename>" format.

import types, sys, re



class JSONSchemaValidator:
  # ALTERNATIVE: Go back to the class based approach and create validators
  #              but make the type validator a special validator that
  #              recursively processes the object definitions.
  
  # ALTERNATIVE: Same as the class based approach but type validator only 
  #              validates the object is an object if it's specified as an
  #              object type. Another driver class would perform the recursive
  #              processing.
  
  # Map of schema types to their equivalent in the python types module
  # TODO: Test support for unicode string types
  typesmap = {
    "string": [types.StringType, types.UnicodeType],
    "integer": types.IntType,
    "number": [types.IntType, types.FloatType],
    "boolean": types.BooleanType,
    "object": types.DictType,
    "array": types.ListType,
    "null": types.NoneType,
    "any": None
  }
  
  # Default schema property values.
  schemadefault = {
    "id": None,
    "type": None,
    "properties": None,
    "items": None,
    "optional": False,
    "additionalProperties": None,
    "requires": None,
    "unique": False,
    "minimum": None,
    "maximum": None,
    "minItems": None,
    "maxItems": None,
    "pattern": None,
    "maxLength": None,
    "minLength": None,
    "enum": None,
    "options": None,
    "readonly": None,
    "title": None,
    "description": None,
    "format": None,
    "default": None,
    "transient": None,
    "maxDecimal": None,
    "hidden": None,
    "disallow": None,
    "extends": None
  }
  
  refmap = {}
  
  def validate_id(self, x, fieldname, schema, ID=None):
    '''Validates a schema id and adds it to the schema reference map'''
    if ID is not None:
      self.refmap[ID] = schema
    return x
  
  def validate_type(self, x, fieldname, schema, fieldtype=None):
    '''Validates that the fieldtype specified is correct for the given
       data'''
    
    converted_fieldtype = self.convert_type(fieldtype)
    value = x.get(fieldname)
    
    if converted_fieldtype is not None and x.get(fieldname) is not None:
      if isinstance(converted_fieldtype, types.ListType):
        # Match if type matches any one of the types in the list
        datavalid = False
        for eachtype in converted_fieldtype:
          try:
            self.validate_type(x, fieldname, eachtype, eachtype)
            datavalid = True
            break
          except ValueError:
            pass
        if not datavalid:
          raise ValueError("Value %s is not of type %s" % (value, repr(fieldtype)))
      else:
        if not isinstance(value, converted_fieldtype):
          raise ValueError("Value %s is not of type %s" % (value, repr(fieldtype)))
    return x
  
  def validate_properties(self, x, fieldname, schema, properties=None):
    return x
  
  def validate_items(self, x, fieldname, schema, items=None):
    return x
  
  def validate_optional(self, x, fieldname, schema, optional=False):
    '''Validates that the given field is present if optional is false'''
    # Make sure the field is present
    if fieldname not in x.keys() and not optional:
      raise ValueError("Required field %s is missing" % fieldname)
    return x
  
  def validate_additionalProperties(self, x, fieldname, schema, properties=None):
    return x
  
  def validate_requires(self, x, fieldname, schema, requires=None):
    if x.get(fieldname) is not None and requires is not None:
      if x.get(requires) is None:
        raise ValueError("%s is required by field %s" % (requires, fieldname))
    return x
  
  def validate_unique(self, x, fieldname, schema, unique=False):
    '''Validates that the given field is unique in the instance object tree'''
    # TODO: Support unique values
    # TODO: What does it mean to be unique in the object tree? If a child node
    #       is marked unique does that mean that parent nodes need to be checked
    #       for uniqueness?
    return x
  
  def validate_minimum(self, x, fieldname, schema, minimum=None):
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
  
  def validate_maximum(self, x, fieldname, schema, maximum=None):
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
  
  def validate_minItems(self, x, fieldname, schema, minitems=None):
    if minitems is not None and x.get(fieldname) is not None:
      value = x.get(fieldname)
      if value is not None:
        if isinstance(value, types.ListType) and len(value) < minitems:
          raise ValueError("%s must have a minimum of %d items" % (fieldname, minitems))
    return x
  
  def validate_maxItems(self, x, fieldname, schema, maxitems=None):
    if maxitems is not None and x.get(fieldname) is not None:
      value = x.get(fieldname)
      if value is not None:
        if isinstance(value, types.ListType) and len(value) > maxitems:
          raise ValueError("%s must have a maximum of %d items" % (fieldname, maxitems))
    return x
  
  def validate_pattern(self, x, fieldname, schema, pattern=None):
    '''Validates that the given field, if a string, matches the given regular
       expression.'''
    value = x.get(fieldname)
    if pattern is not None and \
       value is not None and \
       isinstance(value, types.StringType):
      p = re.compile(pattern)
      if not p.match(value):
        raise ValueError("%s does not match regular expression %s" % (value, pattern))
    return x
  
  def validate_maxLength(self, x, fieldname, schema, length=None):
    '''Validates that the value of the given field is shorter than the specified
       length if a string'''
    value = x.get(fieldname)
    if length is not None and \
       value is not None and \
       isinstance(value, types.StringType) and \
       len(value) > length:
      raise ValueError("Length of '%s' must be more than %f" % (value, length))
    return x
    
  def validate_minLength(self, x, fieldname, schema, length=None):
    '''Validates that the value of the given field is longer than the specified
       length if a string'''
    value = x.get(fieldname)
    if length is not None and \
       value is not None and \
       isinstance(value, types.StringType) and \
       len(value) < length:
      raise ValueError("Length of '%s' must be more than %f" % (value, length))
    return x
  
  def validate_enum(self, x, fieldname, schema, options=None):
    '''Validates that the value of the field is equal to one of the specified
       option values if specified'''
    value = x.get(fieldname)
    if options is not None and value is not None:
      if isinstance(options, types.ListType):
        raise ValueError("Value %s is not in the enumeration: %s" % value, repr(options))
      if value not in options:
        raise ValueError("Enumeration for field '%s' is not a list type", fieldname)
    return x
  
  def validate_options(self, x, fieldname, schema, options=None):
    return x
  
  def validate_readonly(self, x, fieldname, schema, readonly=False):
    return x
  
  def validate_title(self, x, fieldname, schema, title=None):
    if title is not None and \
       not isinstance(title, types.StringType):
      raise ValueError("The title for %s must be a string" % fieldname);
    return x
  
  def validate_description(self, x, fieldname, schema, description=None):
    if description is not None and \
       not isinstance(description, types.StringType):
      raise ValueError("The description for %s must be a string" % fieldname);
    return x
  
  def validate_format(self, x, fieldname, schema, format=None):
    '''Validates that the value of the field matches the predifined format
       specified.'''
    # No definitions are currently defined for formats
    return x
  
  def validate_default(self, x, fieldname, schema, default=None):
    return x
  
  def validate_transient(self, x, fieldname, schema, transient=False):
    return x
  
  def validate_maxDecimal(self, x, fieldname, schema, maxdecimal=None):
    return x
  
  def validate_hidden(self, x, fieldname, schema, hidden=False):
    return x
  
  def validate_disallow(self, x, fieldname, schema, disallow=None):
    '''Validates that the value of the given field does not match the disallowed
       type.'''
    if disallow is not None:
      try:
        self.validate_type(x, fieldname, schema, disallow)
      except ValueError:
        return x
      raise ValueError("Type %s is disallowed for field %s" % (disallow, fieldname))
    return x
  
  def validate_extends(self, x, fieldname, schema, extends=None):
    return x
  
  # def validate_nullable(self, x, fieldname, fieldtype=None, nullable=False):
  #   '''Validates that the given field is not null if the field is present and
  #      nullable is false'''
  #   try:
  #     if fieldname in x.keys() and x.get(fieldname) is None and not nullable:
  #       raise ValueError("%s is not nullable." % fieldname)
  #   except AttributeError, e:
  #     print fieldname
  #     sys.exit()
  #   return x
  
  def checktype(self, fieldtype):
    '''Determines if the type validator can handle the given type'''
    if isinstance(fieldtype, types.TypeType):
      if fieldtype not in self.typesmap.values():
        raise ValueError("Unsupported field type: %s" % fieldtype)
    elif isinstance(fieldtype, types.ListType):
      for mytype in fieldtype:
        if checktype(mytype):
          raise ValueError("Unsupported field type: %s" % mytype)
    else:
      if fieldtype not in self.typesmap.keys():
        raise ValueError("Unsupported field type: %s" % fieldtype)
  
  def convert_type(self, fieldtype):
    if isinstance(fieldtype, types.TypeType):
      return fieldtype
    elif isinstance(fieldtype, types.ListType):
      converted_fields = []
      for subfieldtype in fieldtype:
        converted_fields.append(self.convert_type(subfieldtype))
      return converted_fields
    elif fieldtype is None:
      return None
    else:
      fieldtype = str(fieldtype)
      if fieldtype in self.typesmap.keys():
        return self.typesmap[fieldtype]
      else:
        raise ValueError("Field type %s is not supported." % fieldtype)
  
  def validate(self, data, schema):
    '''Validates a piece of json data against the provided json-schema.'''
    
    #TODO: Validate the schema object here.
    
    self.refmap = {}
    # Wrap the data in a dictionary
    self._validate("_data", {"_data": data}, schema)
  
  def _validate(self, fieldname, data, schema):
    #TODO: Should fields that are not specified in the schema be allowed?
    #      Allowing them for now.
    if schema is not None:
      
      #Initialize defaults
      for schemaprop in self.schemadefault.keys():
        if schemaprop not in schema:
          schema[schemaprop] = self.schemadefault[schemaprop]
      
      for schemaprop in schema:
        # print schemaprop
        validatorname = "validate_"+schemaprop
        
        try:
           validator = getattr(self, validatorname)
           validator(data,fieldname, schema, schema.get(schemaprop))
        except AttributeError:
          raise ValueError("Schema property %s is not supported" % schemaprop)
          
      # if isinstance(data, types.DictType) and schematype:
      #   # recurse!
      #   for key in schematype.keys():
      #     # get the data itself
      #     realdata = data.get(fieldname)
      #     _validate(key, realdata, schematype)
          
    return data

def validate(data, schema):
  validator = JSONSchemaValidator()
  return validator.validate(data,schema)