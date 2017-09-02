from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase
from tests import test_logger

from pyffi.spells import Toaster


class TestToasterOptimisationNif(BaseNifFileTestCase):
    # I didn't need setUp and tearDown here..

    def setUp(self):
        super(TestToasterOptimisationNif, self).setUp()
        self.src_name = "test.nif"
        super(TestToasterOptimisationNif, self).copyFile()

    def test_non_interactive_optimisation(self):
        call_niftoaster("optimize", "--raise", "--noninteractive", "--verbose=1", self.dest_file)
        """ pyffi.toaster:INFO:=== tests/spells/nif/files/out/_test.nif ===
            pyffi.toaster:INFO:  --- fix_delunusedroots & opt_cleanreflists & fix_detachhavoktristripsdata & fix_texturepath & fix_clampmaterialalpha & fix_bhksubshapes & fix_emptyskeletonroots ---
            pyffi.toaster:INFO:    ~~~ NiNode [test] ~~~
            pyffi.toaster:INFO:      ~~~ NiTriShape [Cube] ~~~
            pyffi.toaster:INFO:  --- opt_geometry ---
            pyffi.toaster:INFO:    ~~~ NiNode [test] ~~~
            pyffi.toaster:INFO:      ~~~ NiTriShape [Cube] ~~~
            pyffi.toaster:INFO:        removing duplicate vertices
            pyffi.toaster:INFO:        (num vertices was 8 and is now 8)
            pyffi.toaster:INFO:        optimizing triangle ordering
            pyffi.toaster:INFO:        (ATVR stable at 1.000)
            pyffi.toaster:INFO:        optimizing vertex ordering
            pyffi.toaster:INFO:  --- opt_mergeduplicates ---
            pyffi.toaster:INFO:    ~~~ NiNode [test] ~~~
            pyffi.toaster:INFO:      ~~~ NiTriShape [Cube] ~~~
            pyffi.toaster:INFO:        ~~~ NiTriShapeData [] ~~~
            pyffi.toaster:INFO:  overwriting tests/spells/nif/files/out..._test.nif
            pyffi.toaster:INFO:Finished.
        """

    def test_simulate_user_optimisation(self):
        Toaster.toast.__globals__['input'] = input_func
        call_niftoaster("optimize", "--raise", "--verbose=1", self.dest_file)

inputs = ["yes it is", "n", "y"]  # list of inputs of this test


def input_func(self, msg=""):
    result = inputs.pop(0)
    test_logger.debug("%s%s" % (msg, result))
    return result
