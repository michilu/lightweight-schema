#!/usr/bin/env python
#:coding=utf-8:
#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:

'''
Provides JSON schema validation based on the specifications of the the 
JSON schema proposal (http://www.json.com/json-schema-proposal/).
'''

#TODO: Line numbers for error messages
#TODO: Add checks to make sure the schema itself is valid
#TODO: Support command line validation kind of like how simplejson allows 
#      encoding using the "python -m<modulename>" format.
#TODO: Support encodings other than utf-8

def validate(data, schema):
  '''Validates a parsed json document against the provided schema'''
  from validator import JSONSchemaValidator
  validator = JSONSchemaValidator()
  return validator.validate(data,schema)