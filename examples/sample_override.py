#!/usr/bin/env python
#:coding=utf-8:
#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:

import re
import simplejson
import jsonschema
from jsonschema.validator import JSONSchemaValidator

class FunctionValidator(JSONSchemaValidator):
  '''FunctionValidator extends the JSONSchemaValidator to support Javascript
     functions within JSON schema'''
  def validate_type(self, x, fieldname, schema, fieldtype=None):
    '''Performs very simple validation on the value of the function property to
       make sure it is a Javascript function'''
    if fieldtype == "function":
      r = re.compile("^function")
      value = x.get(fieldname)
      if not r.match(value):
        raise ValueError("Value for field '%s' is not a valid Javascript function definition" % fieldname)
      else:
        return x
    else:
      JSONSchemaValidator.validate_type(self, x, fieldname, schema, fieldtype)

def main():
  import sys
  if len(sys.argv) == 1:
    infile = sys.stdin
    schemafile = sys.stdout
  elif len(sys.argv) == 2:
    if sys.argv[1] == "--help":
      raise SystemExit("%s [infile [schemafile]]" % (sys.argv[0],))
    infile = open(sys.argv[1], 'rb')
    schemafile = sys.stdout
  elif len(sys.argv) == 3:
    infile = open(sys.argv[1], 'rb')
    schemafile = open(sys.argv[2], 'rb')
  else:
    raise SystemExit("%s [infile [schemafile]]" % (sys.argv[0],))
  try:
    obj = simplejson.load(infile)
    schema = simplejson.load(schemafile)
    jsonschema.validate(obj, schema, validator_cls=FunctionValidator)
  except ValueError, e:
    raise SystemExit(e)

if __name__=='__main__':
  main()
