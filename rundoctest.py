import sys
import unittest
import doctest

import PyFFI
import PyFFI.Common
import PyFFI.Bases.Basic
import PyFFI.Bases.Struct
import PyFFI.Bases.Expression
import PyFFI.Utils
import PyFFI.Utils.PyTriStrip
import PyFFI.NIF
import PyFFI.NIF.NiTriStripsData
import PyFFI.NIF.NiTriShapeData
import PyFFI.NIF.NiGeometry
import PyFFI.NIF.NiNode
import PyFFI.CGF

mods = [ val for (key, val) in sys.modules.iteritems() if key.startswith('PyFFI') ]

suite = unittest.TestSuite()
for mod in mods:
    try:
        suite.addTest(doctest.DocTestSuite(mod))
    except ValueError: # no tests
        pass
runner = unittest.TextTestRunner(verbosity=10)
runner.run(suite)
