from tests.utils import BaseNifFileTestCase
from nose.tools import assert_equals, assert_is
from pyffi.spells.nif.optimize import SpellDelUnusedBones


class TestDeleteUnusedBonesOptimisationNif(BaseNifFileTestCase):
    """Tests for the opt_delunusedbones spell"""

    def setUp(self):
        super(TestDeleteUnusedBonesOptimisationNif, self).setUp()
        self.src_name = "test_opt_delunusedbones.nif"
        super(TestDeleteUnusedBonesOptimisationNif, self).copyFile()
        super(TestDeleteUnusedBonesOptimisationNif, self).readNifData()

    def test_unused_bone_deletion(self):
        # check dummy bone
        assert_equals(self.data.roots[0].children[0].children[0].name, b'Test')

        # run the spell that fixes this
        spell = SpellDelUnusedBones(data=self.data)
        spell.recurse()
        """
        pyffi.toaster:INFO:--- opt_delunusedbones ---
        pyffi.toaster:INFO:  ~~~ NiNode [Bip01] ~~~
        pyffi.toaster:INFO:    ~~~ NiNode [Bip01 Pelvis] ~~~
        pyffi.toaster:INFO:      ~~~ NiNode [Test] ~~~
        pyffi.toaster:INFO:        removing unreferenced bone
        pyffi.toaster:INFO:      ~~~ NiNode [Dummy] ~~~
        pyffi.toaster:INFO:        ~~~ NiNode [Bip01 Spine] ~~~
        pyffi.toaster:INFO:          ~~~ NiNode [Bip01 Spine1] ~~~
        pyffi.toaster:INFO:            ~~~ NiNode [Bip01 Spine2] ~~~
        pyffi.toaster:INFO:              ~~~ NiNode [Bip01 Neck] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 Head] ~~~
        pyffi.toaster:INFO:                  ~~~ NiNode [Bip01 Brain] ~~~
        pyffi.toaster:INFO:                    removing unreferenced bone
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 L Clavicle] ~~~
        pyffi.toaster:INFO:                  ~~~ NiNode [Bip01 L UpperArm] ~~~
        pyffi.toaster:INFO:                    ~~~ NiNode [Bip01 L Forearm] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 R Clavicle] ~~~
        pyffi.toaster:INFO:                  ~~~ NiNode [Bip01 R UpperArm] ~~~
        pyffi.toaster:INFO:                    ~~~ NiNode [Bip01 R Forearm] ~~~
        pyffi.toaster:INFO:          ~~~ NiNode [Bip01 L Thigh] ~~~
        pyffi.toaster:INFO:            ~~~ NiNode [Bip01 L Calf] ~~~
        pyffi.toaster:INFO:              ~~~ NiNode [Bip01 L Foot] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 L Toe0] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 L Toe1] ~~~
        pyffi.toaster:INFO:                  removing unreferenced bone
        pyffi.toaster:INFO:          ~~~ NiNode [Bip01 R Thigh] ~~~
        pyffi.toaster:INFO:            ~~~ NiNode [Bip01 R Calf] ~~~
        pyffi.toaster:INFO:              ~~~ NiNode [Bip01 R Foot] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 R Toe0] ~~~
        """
        # check that dummy bone is gone
        assert_is(self.data.roots[0].children[0].children[0], None)
