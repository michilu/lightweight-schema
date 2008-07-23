import math
from unittest import TestCase

import jsonschema

class TestType(TestCase):
    def test_integer(self):
      for x in [1, 89, 48, 32, 49, 42]:
        jsonschema.validate(x, {"type":"integer"})
      
      #failures
      for x in [1.2, "bad", {"test":"blah"}, [32, 49], None, True]:
        try:
          jsonschema.validate(x, {"type":"integer"})
        except ValueError:
          pass
        else:
          self.fail("Expected failure for %s" % repr(x))
    
    def test_string(self):
      for x in ["surrender?", "nuts!", "ok", "@hsuha", "\'ok?\'", "blah"]:
        jsonschema.validate(x, {"type":"string"})
      
      #failures
      for x in [1.2, 1, {"test":"blah"}, [32, 49], None, True]:
        try:
          jsonschema.validate(x, {"type":"string"})
        except ValueError:
          pass
        else:
          self.fail("Expected failure for %s" % repr(x))