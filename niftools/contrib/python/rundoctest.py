import unittest
import doctest
import NifFormat.NifFormat
import FileFormat.Bases.Compound
import FileFormat.Bases.Expression

suite = unittest.TestSuite()
for mod in [ NifFormat.NifFormat, FileFormat.Bases.Compound, FileFormat.Bases.Expression ]:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
