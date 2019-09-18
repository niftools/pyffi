"""Tests for the fix_detachhavoktristripsdata spell"""
from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase

from pyffi.spells.nif.fix import SpellDetachHavokTriStripsData

from nose.tools import assert_equals, assert_true, assert_false


class TestDetachHavokTriStripsDataNif(BaseNifFileTestCase):
    """Invoke the fix_detachhavoktristripsdata spell check through nif toaster"""

    def setUp(self):
        super(TestDetachHavokTriStripsDataNif, self).setUp()
        self.src_name = "test_fix_detachhavoktristripsdata.nif"
        super(TestDetachHavokTriStripsDataNif, self).copyFile()
        super(TestDetachHavokTriStripsDataNif, self).readNifData()

    def test_explicit_detach_havok_tristripsdata(self):
        """run the spell that detaches the trishapedata"""

        # check that data is shared
        assert_true(self.data.roots[0].children[0].collision_object.body.shape.sub_shapes[0].strips_data[0] \
                    is self.data.roots[0].children[0].data)

        s = SpellDetachHavokTriStripsData(data=self.data)
        s.recurse()

        # check that data is no longer shared
        assert_false(self.data.roots[0].children[0].collision_object.body.shape.sub_shapes[0].strips_data[0]
                     is self.data.roots[0].children[0].data)

    def test_non_interactive_fix_string_palette(self):
        call_niftoaster("--raise", "fix_detachhavoktristripsdata", "--dry-run", "--noninteractive", "--verbose=1",
                        self.dest_file)
        """
        pyffi.toaster:INFO:=== tests/spells/nif/files/test_fix_detachhavoktristripsdata.nif ===
        pyffi.toaster:INFO:  --- fix_detachhavoktristripsdata ---
        pyffi.toaster:INFO:    ~~~ NiNode [MiddleWolfRug01] ~~~
        pyffi.toaster:INFO:      ~~~ NiTriStrips [MiddleWolfRug01:0] ~~~
        pyffi.toaster:INFO:        ~~~ bhkCollisionObject [] ~~~
        pyffi.toaster:INFO:          ~~~ bhkRigidBodyT [] ~~~
        pyffi.toaster:INFO:            ~~~ bhkListShape [] ~~~
        pyffi.toaster:INFO:              ~~~ bhkNiTriStripsShape [] ~~~
        pyffi.toaster:INFO:                detaching havok data
        pyffi.toaster:INFO:  writing to temporary file
        pyffi.toaster:INFO:Finished.
        """
