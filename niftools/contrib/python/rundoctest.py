import unittest
import doctest
import NifFormat.NifFormat
import FileFormat.Bases.Compound

suite = unittest.TestSuite()
for mod in [ NifFormat.NifFormat, FileFormat.Bases.Compound ]:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
