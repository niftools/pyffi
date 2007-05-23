import unittest
import doctest
import NifFormat.NifFormat
import NifFormat.BasicTypes
import FileFormat.Bases.Basic
import FileFormat.Bases.Compound
import FileFormat.Bases.Expression
import FileFormat.HexDump

suite = unittest.TestSuite()
for mod in [ NifFormat.NifFormat, NifFormat.BasicTypes, FileFormat.Bases.Basic, FileFormat.Bases.Compound, FileFormat.Bases.Expression, FileFormat.HexDump ]:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
