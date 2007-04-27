import unittest
import doctest
import NifFormat.NifFormat
import NifFormat.BasicTypes
import FileFormat.Bases.Compound
import FileFormat.Bases.Expression

suite = unittest.TestSuite()
for mod in [ NifFormat.NifFormat, NifFormat.BasicTypes, FileFormat.Bases.Compound, FileFormat.Bases.Expression ]:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
