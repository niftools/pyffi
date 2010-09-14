import doctest
import logging
import sys
import unittest

import pyffi
import pyffi.object_models.common
import pyffi.object_models
import pyffi.object_models.xml
import pyffi.object_models.mex
import pyffi.object_models.any_type
import pyffi.object_models.simple_type
import pyffi.object_models.array_type
import pyffi.object_models.binary_type
import pyffi.object_models.xml.basic
import pyffi.object_models.xml.bit_struct
import pyffi.object_models.xml.enum
import pyffi.object_models.xml.expression
import pyffi.object_models.xml.struct_
import pyffi.utils
import pyffi.utils.tristrip
import pyffi.utils.mathutils
import pyffi.utils.quickhull
import pyffi.utils.inertia
import pyffi.utils.tangentspace
import pyffi.utils.mopp
import pyffi.formats.nif
import pyffi.formats.cgf
import pyffi.formats.kfm
import pyffi.formats.dds
import pyffi.formats.tga
import pyffi.formats.egm
import pyffi.formats.esp
import pyffi.formats.tri
import pyffi.formats.bsa
import pyffi.formats.egt
import pyffi.spells
import pyffi.spells.nif
import pyffi.spells.nif.fix
import pyffi.spells.nif.modify
import pyffi.spells.nif.check
# these two do not yet work on py3k
if sys.version_info[0] < 3:
    import pyffi.object_models.xsd
    import pyffi.formats.dae

# force number of jobs to be 1 (multithreading makes doctesting difficult)
pyffi.spells.Toaster.DEFAULT_OPTIONS["jobs"] = 1

mods = [val for (key, val) in sys.modules.iteritems()
        if key.startswith('pyffi')]

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
suite.addTest(doctest.DocFileSuite('tests/nif/modify_delbranches.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/modify_delvertexcolor.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/fix_cleanstringpalette.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/modify_substitutestringpalette.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/modify_allbonepriorities.txt'))
suite.addTest(doctest.DocFileSuite('tests/om_simpletype.txt'))
suite.addTest(doctest.DocFileSuite('tests/om_arraytype.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/matrix.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/skinpartition.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/bhkpackednitristripsshape.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/opt_delunusedbones.txt'))
suite.addTest(doctest.DocFileSuite('tests/nif/opt_collisiongeometry.txt'))
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

