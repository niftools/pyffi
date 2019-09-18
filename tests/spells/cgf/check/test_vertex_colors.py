"""Regression test for vertex color spells"""
from tests.scripts.cgf import call_cgftoaster
from tests.utils import BaseCgfFileTestCase


class TestCheckVertexColorCgf(BaseCgfFileTestCase):
    """Invoke the check_vcols spell check through cgf toaster"""

    def setUp(self):
        super(TestCheckVertexColorCgf, self).setUp()
        self.src_name = "monkey.cgf"
        super(TestCheckVertexColorCgf, self).copyFile()
        super(TestCheckVertexColorCgf, self).readCgfData()

    def test_non_interactive_check_vcols(self):
        """Check the vertex color spell"""
        call_cgftoaster("--raise", "check_vcols", "--noninteractive", "--verbose=1", self.dest_file)
        """
        pyffi.toaster:INFO:=== tests/formats/cgf/monkey.cgf ===
        pyffi.toaster:INFO:  --- check_vcols ---
        pyffi.toaster:INFO:    ~~~ NodeChunk [Merged] ~~~
        pyffi.toaster:INFO:      ~~~ MeshChunk [] ~~~
        pyffi.toaster:INFO:    ~~~ NodeChunk [CryExportNode_monkey-CGF-monkey-DoExport-MergeNodes] ~~~
        pyffi.toaster:INFO:Finished.
        """


class TestCheckVColCgf(BaseCgfFileTestCase):
    """Invoke the check_vcols spell check through cgf toaster"""

    def setUp(self):
        super(TestCheckVColCgf, self).setUp()
        self.src_name = "vcols.cgf"
        super(TestCheckVColCgf, self).copyFile()
        super(TestCheckVColCgf, self).readCgfData()

    def test_non_interactive_check_vcols(self):
        """Check the vertex color spell"""
        call_cgftoaster("--raise", "check_vcols", "--noninteractive", "--verbose=1", self.dest_file)
        """
        pyffi.toaster:INFO:=== tests/formats/cgf/vcols.cgf ===
        pyffi.toaster:INFO:  --- check_vcols ---
        pyffi.toaster:INFO:    ~~~ NodeChunk [Monkey] ~~~
        pyffi.toaster:INFO:      ~~~ MeshChunk [] ~~~
        pyffi.toaster:INFO:        has vertex colors!
        pyffi.toaster:INFO:Finished.
        """