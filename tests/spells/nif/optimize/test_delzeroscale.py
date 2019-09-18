from tests.utils import BaseNifFileTestCase
from nose.tools import assert_true
from tests import test_logger
import pyffi
from tests.utils import BaseNifFileTestCase
from pyffi.spells.nif.optimize import SpellDelZeroScale

class TestDelZeroScaleOptimisationNif(BaseNifFileTestCase):
    """Test for the delete zero scale spell"""

    def setUp(self):
        super(TestDelZeroScaleOptimisationNif, self).setUp()
        self.src_name = "test_opt_zeroscale.nif"
        super(TestDelZeroScaleOptimisationNif, self).copyFile()
        super(TestDelZeroScaleOptimisationNif, self).readNifData()

    def test_zero_scale_deletion(self):
        # check zero scale
        children = self.data.roots[0].children[0].children
        assert_true(len(children), 4)
        for child in children:
            test_logger.debug("{0}, {1}".format(child.name, child.scale))

        # run the spell that fixes this
        spell = SpellDelZeroScale(data=self.data)
        spell.recurse()
        """
        pyffi.toaster:INFO:--- opt_delzeroscale ---
        pyffi.toaster:INFO:  ~~~ NiNode [Scene Root] ~~~
        pyffi.toaster:INFO:    ~~~ NiNode [Cone] ~~~
        pyffi.toaster:INFO:      ~~~ NiTriShape [Tri Cone 0] ~~~
        pyffi.toaster:INFO:      ~~~ NiTriShape [Tri Cone 1] ~~~
        pyffi.toaster:INFO:        removing zero scaled branch
        pyffi.toaster:INFO:      ~~~ NiTriShape [Tri Cone 2] ~~~
        pyffi.toaster:INFO:        removing zero scaled branch
        pyffi.toaster:INFO:      ~~~ NiTriShape [Tri Cone 3] ~~~
        """

        # check that zero scale nodes are gone
        children = self.data.roots[0].children[0].children
        for child in children:
            if child:
                test_logger.debug("{0}, {1}".format(child.name, child.scale))
        assert_true(len(children), 2)
