"""Tests for the modify_substitutestringpalette spell"""
from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase

from nose.tools import assert_true


class TestModifySubstitutePaletteNif(BaseNifFileTestCase):
    """Invoke the modify_substitutestringpalette spell check through nif toaster"""

    def setUp(self):
        super(TestModifySubstitutePaletteNif, self).setUp()
        self.src_name = "test_fix_cleanstringpalette.nif"
        super(TestModifySubstitutePaletteNif, self).copyFile()
        super(TestModifySubstitutePaletteNif, self).readNifData()

    def test_non_interactive_modify_string_palette_values(self):
        """Test that we can modify the string palette values"""
        strings = self.data.roots[0].controller.controller_sequences[0].string_palette.palette.get_all_strings()
        expected = [b'Test', b'Hello', b'People', b'NiTransformController', b'Test NonAccum', b'Useless', b'Crap']
        assert_true(strings, expected)

        # substitute
        call_niftoaster("--raise", "modify_substitutestringpalette", "-a", "/Test/Woops", "--noninteractive", "--verbose=1", self.dest_file)

        """
        pyffi.toaster:INFO:=== tests/spells/nif/files...test_fix_cleanstringpalette.nif ===
        pyffi.toaster:INFO:  --- modify_substitutestringpalette ---
        pyffi.toaster:INFO:    ~~~ NiNode [TestCleanStringPalette] ~~~
        pyffi.toaster:INFO:      ~~~ NiControllerManager [] ~~~
        pyffi.toaster:INFO:        parsing string palette
        pyffi.toaster:INFO:        b'Test' -> b'Woops'
        pyffi.toaster:INFO:        b'Test NonAccum' -> b'Woops NonAccum'
        pyffi.toaster:INFO:        b'Test' -> b'Woops'
        pyffi.toaster:INFO:        b'Test NonAccum' -> b'Woops NonAccum'
        pyffi.toaster:INFO:  writing tests/spells/nif/files..._test_fix_cleanstringpalette.nif
        pyffi.toaster:INFO:Finished.
        """

        super(TestModifySubstitutePaletteNif, self).readNifData()

        # check cleaned palette
        strings = self.data.roots[0].controller.controller_sequences[0].string_palette.palette.get_all_strings()
        expected = [b'Woops', b'NiTransformController', b'Woops NonAccum']
        assert_true(strings, expected)
