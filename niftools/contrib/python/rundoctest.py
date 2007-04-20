import unittest
import doctest
import NifFormat.NifFormat

suite = unittest.TestSuite()
for mod in [ NifFormat.NifFormat ]:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
