"""Tests for the fix_texturepath spell"""
from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase, assert_tuple_values

class TestFixTangentSpaceNif(BaseNifFileTestCase):
    """Invoke the fix_texturepath spell check through nif toaster"""

    def setUp(self):
        super(TestFixTangentSpaceNif, self).setUp()
        self.src_name = "test_fix_texturepath.nif"
        super(TestFixTangentSpaceNif, self).copyFile()
        super(TestFixTangentSpaceNif, self).readNifData()

    def test_non_interactive_fix_texture_path(self):
        call_niftoaster("--raise", "fix_texturepath", "fix_addtangentspace", "--dry-run", "--noninteractive",
                        "--verbose=1", self.dest_file)

        """
        pyffi.toaster:INFO:=== tests/spells/nif/files/test_fix_texturepath.nif ===
        pyffi.toaster:INFO:  --- fix_texturepath ---
        pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
        pyffi.toaster:INFO:      ~~~ NiTriStrips [Sphere] ~~~
        pyffi.toaster:INFO:        ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:          ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:            fixed file name 'path\test1.dds'
        pyffi.toaster:INFO:          ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:            fixed file name 'an\other\path\also\backslashes\test2.dds'
        pyffi.toaster:INFO:          ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:          ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:            fixed file name 'evil\rants\IS\not\good\no\no\test4.dds'
        pyffi.toaster:INFO:          ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:          ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:            fixed file name 'doubleslash\test6.dds'
        pyffi.toaster:INFO:  writing to temporary file
        pyffi.toaster:INFO:Finished.
        """

