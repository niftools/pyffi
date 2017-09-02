"""Regression test for tangent space algorithm"""
from tests.scripts.cgf import call_cgftoaster
from tests.utils import BaseCgfFileTestCase


class TestCheckTangentSpaceCgf(BaseCgfFileTestCase):
    """Invoke the fix_texturepath spell check through nif toaster"""

    def setUp(self):
        super(TestCheckTangentSpaceCgf, self).setUp()
        self.src_name = "monkey.cgf"
        super(TestCheckTangentSpaceCgf, self).copyFile()
        super(TestCheckTangentSpaceCgf, self).readCgfData()

    def test_non_interactive_check_tangentspace(self):
        """Check_tangentspace spell"""
        call_cgftoaster("--raise", "check_tangentspace",  "--noninteractive", "--verbose=1", self.dest_file)
        """
        pyffi.toaster:INFO:=== tests/formats/cgf/monkey.cgf ===
        pyffi.toaster:INFO:  --- check_tangentspace ---
        pyffi.toaster:INFO:    ~~~ NodeChunk [Merged] ~~~
        pyffi.toaster:INFO:      ~~~ MeshChunk [] ~~~
        pyffi.toaster:INFO:        recalculating new tangent space
        pyffi.toaster:INFO:        validating and checking old with new
        pyffi.toaster:WARNING:...
        ...
        pyffi.toaster:INFO:    ~~~ NodeChunk [CryExportNode_monkey-CGF-monkey-DoExport-MergeNodes] ~~~
        pyffi.toaster:INFO:Finished.
        """