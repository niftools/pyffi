import sys
import unittest
import doctest

import PyFFI
import PyFFI.Common
import PyFFI.ObjectModels.FileFormat
import PyFFI.ObjectModels.XML.FileFormat
import PyFFI.ObjectModels.XSD.FileFormat
import PyFFI.ObjectModels.SimpleType
import PyFFI.ObjectModels.ArrayType
import PyFFI.ObjectModels.XML.Basic
import PyFFI.ObjectModels.XML.Struct
import PyFFI.ObjectModels.XML.Expression
import PyFFI.Utils
import PyFFI.Utils.TriStrip
import PyFFI.Utils.MathUtils
import PyFFI.Utils.QuickHull
import PyFFI.Utils.Inertia
import PyFFI.Utils.TangentSpace
import PyFFI.Utils.Mopp
import PyFFI.Formats.NIF
import PyFFI.Formats.NIF.NiGeometryData
import PyFFI.Formats.NIF.NiTriStripsData
import PyFFI.Formats.NIF.NiTriShapeData
import PyFFI.Formats.NIF.NiGeometry
import PyFFI.Formats.NIF.NiObjectNET
import PyFFI.Formats.NIF.NiNode
import PyFFI.Formats.NIF.NiSkinData
import PyFFI.Formats.NIF.StringPalette
import PyFFI.Formats.NIF.ControllerLink
import PyFFI.Formats.NIF.NiBSplineData
import PyFFI.Formats.CGF
import PyFFI.Formats.CGF.MeshChunk
import PyFFI.Formats.KFM
import PyFFI.Formats.DDS
import PyFFI.Formats.TGA
import PyFFI.Formats.DAE

mods = [val for (key, val) in sys.modules.iteritems()
        if key.startswith('PyFFI')]

suite = unittest.TestSuite()
for mod in mods:
    try:
        suite.addTest(doctest.DocTestSuite(mod))
    except ValueError: # no tests
        pass

# various regression tests (outside documentation)
suite.addTest(doctest.DocFileSuite('tests/nif/niftoaster.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/optimize.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/dump_tex.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/ffvt3rskin.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/fix_texturepath.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/fix_tangentspace_series_parallel.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/fix_detachhavoktristripsdata.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/fix_clampmaterialalpha.txt'))
suite.addTest(doctest.DocFileSuite('tests/om_simpletype.txt'))
suite.addTest(doctest.DocFileSuite('tests/om_arraytype.txt'))

# TODO: examples
#suite.addTest(doctest.DocFileSuite('examples/*.txt'))

runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
