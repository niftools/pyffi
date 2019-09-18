"""Tests for the fix_texturepath spell"""
from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase

from pyffi.spells.nif.fix import SpellClampMaterialAlpha

from nose.tools import assert_true, assert_equals


class TestFixTexturePathToasterNif(BaseNifFileTestCase):
    """Invoke the fix_texturepath spell check through nif toaster"""

    def setUp(self):
        super(TestFixTexturePathToasterNif, self).setUp()
        self.src_name = "test_fix_clampmaterialalpha.nif"
        super(TestFixTexturePathToasterNif, self).copyFile()
        super(TestFixTexturePathToasterNif, self).readNifData()
        assert_true(self.data.roots[0].children[0].children[0].properties[0].alpha > 1.01)
        assert_true(self.data.roots[0].children[0].children[1].properties[0].alpha < -0.01)

    def test_explicit_fix_texture_path(self):
        """run the spell that fixes texture path"""

        spell = SpellClampMaterialAlpha(data=self.data)
        spell.recurse()

        # check that material alpha are no longer out of range
        assert_equals(self.data.roots[0].children[0].children[0].properties[0].alpha, 1.0)
        assert_equals(self.data.roots[0].children[0].children[1].properties[0].alpha, 0.0)

    def test_non_interactive_fix_clamp_material_alpha(self):

        call_niftoaster("--raise", "fix_clampmaterialalpha", "--dry-run", "--noninteractive", "--verbose=1", self.dest_file)

        """
        pyffi.toaster:INFO:=== tests/spells/nif/files/test_fix_clampmaterialalpha.nif ===
        pyffi.toaster:INFO:  --- fix_clampmaterialalpha ---
        pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
        pyffi.toaster:INFO:      ~~~ NiNode [Cone] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriShape [Tri Cone 0] ~~~
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Red] ~~~
        pyffi.toaster:INFO:            clamping alpha value (1000.000000 -> 1.0)
        pyffi.toaster:INFO:        ~~~ NiTriShape [Tri Cone 1] ~~~
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Green] ~~~
        pyffi.toaster:INFO:            clamping alpha value (-1000.000000 -> 0.0)
        pyffi.toaster:INFO:        ~~~ NiTriShape [Tri Cone 2] ~~~
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Blue] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriShape [Tri Cone 3] ~~~
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Yellow] ~~~
        pyffi.toaster:INFO:  writing to temporary file
        pyffi.toaster:INFO:Finished.
        """
