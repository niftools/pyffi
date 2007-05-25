import unittest
import doctest
import NifFormat.NifFormat
import NifFormat.BasicTypes
import FileFormat.Bases.Basic
import FileFormat.Bases.Compound
import FileFormat.Bases.Expression
import FileFormat.HexDump
import NifFormat.PyTriStrip.PyTriStrip

suite = unittest.TestSuite()
for mod in [ NifFormat.NifFormat, NifFormat.BasicTypes, FileFormat.Bases.Basic, FileFormat.Bases.Compound, FileFormat.Bases.Expression, FileFormat.HexDump, NifFormat.PyTriStrip.PyTriStrip ]:
    suite.addTest(doctest.DocTestSuite(mod))
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
