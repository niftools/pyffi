import doctest
import logging
import sys
import unittest

import PyFFI
import PyFFI.object_models.Common
import PyFFI.object_models
import PyFFI.object_models.xsd
import PyFFI.object_models.xml
import PyFFI.object_models.mex
import PyFFI.object_models.AnyType
import PyFFI.object_models.SimpleType
import PyFFI.object_models.ArrayType
import PyFFI.object_models.BinaryType
import PyFFI.object_models.xml.Basic
import PyFFI.object_models.xml.Struct
import PyFFI.object_models.xml.Expression
import PyFFI.utils
import PyFFI.utils.tristrip
import PyFFI.utils.mathutils
import PyFFI.utils.quickhull
import PyFFI.utils.inertia
import PyFFI.utils.tangentspace
import PyFFI.utils.mopp
import PyFFI.Formats.NIF
import PyFFI.Formats.CGF
import PyFFI.Formats.KFM
import PyFFI.Formats.DDS
import PyFFI.Formats.TGA
import PyFFI.Formats.DAE
import PyFFI.spells

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
suite.addTest(doctest.DocFileSuite('tests/nif/opt_mergeduplicates.txt'))
suite.addTest(doctest.DocFileSuite('tests/om_simpletype.txt'))
suite.addTest(doctest.DocFileSuite('tests/om_arraytype.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/matrix.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/skinpartition.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/bhkpackednitristripsshape.txt'))
suite.addTest(doctest.DocFileSuite('tests/cgf/cgftoaster.txt'))
suite.addTest(doctest.DocFileSuite('tests/kfm/kfmtoaster.txt'))
suite.addTest(doctest.DocFileSuite('docs-sphinx/intro.rst'))

# TODO: examples
#suite.addTest(doctest.DocFileSuite('examples/*.txt'))

# set up logger

# this is a hack for StreamHandler to make it work with doctest
# see http://mail.python.org/pipermail/python-list/2007-January/423842.html
class WrapStdOut(object):
    def __getattr__(self, name):
        return getattr(sys.stdout, name)

logger = logging.getLogger("pyffi")
logger.setLevel(logging.INFO) # skip debug messages
loghandler = logging.StreamHandler(WrapStdOut())
loghandler.setLevel(logging.DEBUG)
logformatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
loghandler.setFormatter(logformatter)
logger.addHandler(loghandler)

# run tests
unittest.TextTestRunner(verbosity=10).run(suite)

