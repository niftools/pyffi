import os.path
from os.path import dirname
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
import pyffi.utils.vertex_cache
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
import pyffi.formats.psk
import pyffi.formats.rockstar.dir_
import pyffi.spells
import pyffi.spells.nif
import pyffi.spells.nif.fix
import pyffi.spells.nif.modify
import pyffi.spells.nif.check
import pyffi.spells.nif.dump
# these two do not yet work on py3k
if sys.version_info[0] < 3:
    import pyffi.object_models.xsd
    import pyffi.formats.dae


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

# force number of jobs to be 1 (multithreading makes doctesting difficult)
pyffi.spells.Toaster.DEFAULT_OPTIONS["jobs"] = 1

mods = [val for (key, val) in sys.modules.items()
        if key.startswith('pyffi')]

for mod in mods:
    try:
        pass
        # suite.addTest(doctest.DocTestSuite(mod))
    except ValueError:  # no tests
        pass

suite = unittest.TestSuite()

filepaths = {'object_model/simpletype.txt',
             'object_model/arraytype.txt',
             'formats/nif/matrix.txt',
             'formats/nif/skinpartition.txt',
             'formats/cgf/cgftoaster.txt',
             'spells/nif/dump_tex.txt',
             'spells/nif/ffvt3rskin.txt',
             'spells/nif/fix_clampmaterialalpha.txt',
             'spells/nif/fix_cleanstringpalette.txt',
             'spells/nif/fix_detachhavoktristripsdata.txt',
             'spells/nif/fix_tangentspace.txt',
             'spells/nif/fix_tangentspace_series_parallel.txt',
             'spells/nif/fix_texturepath.txt',
             'spells/nif/modify_allbonepriorities.txt',
             'spells/nif/modify_delbranches.txt',
             'spells/nif/modify_delvertexcolor.txt',
             'spells/nif/modify_substitutestringpalette.txt',
             'spells/nif/optimize.txt',
             'spells/nif/opt_delunusedbones.txt',

             # Contain outstanding issues
             # 'spells/egm/optimize.txt',
             #'spells/nif/opt_mergeduplicates.txt', #nitrishape issue
             #'formats/nif/niftoaster.txt', #havoklayer issue
             #'formats/nif/bhkpackednitristripsshape.txt', #havoklayer issue

             # 'spells/nif/opt_delzeroscale.txt',
             # 'spells/nif/opt_collisiongeometry.txt',
             # 'spells/nif/opt_collision_to_box_shape.txt',
             # 'spells/nif/opt_vertex_cache.txt',
             # 'tests/kfm/kfmtoaster.txt',
             # 'docs-sphinx/intro.rst',
             }



# various regression tests (outside documentation)

for relpath in filepaths:
    suite.addTest(doctest.DocFileSuite(relpath))

# TODO: examples
# suite.addTest(doctest.DocFileSuite('examples/*.txt'))

def test():
    # run tests
    unittest.TextTestRunner(verbosity=10).run(suite)

