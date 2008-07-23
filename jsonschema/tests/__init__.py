import unittest
import doctest

def additional_tests():
    import jsonschema
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(jsonschema))
    return suite

def main():
    suite = unittest.TestSuite()
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    main()