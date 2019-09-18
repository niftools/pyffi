"""Tests for the fix_cleanstringpalette spell"""
from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase

from pyffi.spells.nif.fix import SpellCleanStringPalette

from nose.tools import assert_equals


class TestFixTexturePathToasterNif(BaseNifFileTestCase):
    """Invoke the fix_texturepath spell check through nif toaster"""


    def setUp(self):
        super(TestFixTexturePathToasterNif, self).setUp()
        self.src_name = "test_fix_cleanstringpalette.nif"
        super(TestFixTexturePathToasterNif, self).copyFile()
        super(TestFixTexturePathToasterNif, self).readNifData()

        # check current string palette
        strings = self.data.roots[0].controller.controller_sequences[0].string_palette.palette.get_all_strings()
        expected = [b'Test', b'Hello', b'People', b'NiTransformController', b'Test NonAccum', b'Useless', b'Crap']
        assert_equals(strings, expected)

    def test_explicit_fix_string_palette(self):
        """run the spell that fixes texture path"""

        spell = SpellCleanStringPalette(data=self.data)
        spell.recurse()

        strings = self.data.roots[0].controller.controller_sequences[0].string_palette.palette.get_all_strings()
        expected = [b'Test', b'NiTransformController', b'Test NonAccum']
        assert_equals(strings, expected)

    def test_non_interactive_fix_string_palette(self):
        call_niftoaster("--raise", "fix_cleanstringpalette", "--dry-run", "--noninteractive", "--verbose=1", self.dest_file)
