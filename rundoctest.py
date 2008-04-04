import sys
import unittest
import doctest

import PyFFI
import PyFFI.Common
import PyFFI.Bases.Basic
import PyFFI.Bases.Struct
import PyFFI.Bases.Expression
import PyFFI.Utils
import PyFFI.Utils.TriStrip
import PyFFI.Utils.MathUtils
import PyFFI.Utils.QuickHull
import PyFFI.Utils.Inertia
import PyFFI.Utils.TangentSpace
import PyFFI.NIF
import PyFFI.NIF.NiTriStripsData
import PyFFI.NIF.NiTriShapeData
import PyFFI.NIF.NiGeometry
import PyFFI.NIF.NiNode
import PyFFI.NIF.NiSkinData
import PyFFI.NIF.StringPalette
import PyFFI.NIF.ControllerLink
import PyFFI.NIF.NiBSplineData
import PyFFI.CGF
import PyFFI.CGF.MeshChunk
import PyFFI.KFM
import PyFFI.DDS
import PyFFI.TGA

mods = [ val for (key, val) in sys.modules.iteritems() if key.startswith('PyFFI') ]

suite = unittest.TestSuite()
for mod in mods:
    try:
        suite.addTest(doctest.DocTestSuite(mod))
    except ValueError: # no tests
        pass
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
