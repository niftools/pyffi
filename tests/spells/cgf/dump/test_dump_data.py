"""Tests for the dump spell for cgf"""
from tests.utils import BaseCgfFileTestCase
from tests.scripts.cgf import call_cgftoaster


class TestDumpDataCgf(BaseCgfFileTestCase):
    """Invoke the dump spell check through cgf toaster"""

    def setUp(self):
        super(TestDumpDataCgf, self).setUp()
        self.src_name = "test.cgf"
        super(TestDumpDataCgf, self).copyFile()
        super(TestDumpDataCgf, self).readCgfData()

    def test_non_interactive_dump(self):
        """Test that we extract texture and material information"""

        call_cgftoaster("--raise", "dump", "--noninteractive", "--verbose=1", self.dest_file)
        """
        pyffi.toaster:INFO:=== tests/scripts/cgf/files/test.cgf ===
        pyffi.toaster:INFO:  --- dump ---
        pyffi.toaster:INFO:    ~~~ SourceInfoChunk [] ~~~
        pyffi.toaster:INFO:      <class 'pyffi.formats.cgf.SourceInfoChunk'> instance at 0x...
        pyffi.toaster:INFO:      * source_file : <None>
        pyffi.toaster:INFO:      * date : Fri Sep 28 22:40:44 2007
        pyffi.toaster:INFO:      * author : blender@BLENDER
        pyffi.toaster:INFO:
        pyffi.toaster:INFO:    ~~~ TimingChunk [GlobalRange] ~~~
        pyffi.toaster:INFO:      <class 'pyffi.formats.cgf.TimingChunk'> instance at 0x...
        pyffi.toaster:INFO:      * secs_per_tick : 0.0002083...
        pyffi.toaster:INFO:      * ticks_per_frame : 160
        pyffi.toaster:INFO:      * global_range :
        pyffi.toaster:INFO:          <class 'pyffi.formats.cgf.RangeEntity'> instance at 0x...
        pyffi.toaster:INFO:          * name : GlobalRange
        pyffi.toaster:INFO:          * start : 0
        pyffi.toaster:INFO:          * end : 100
        pyffi.toaster:INFO:      * num_sub_ranges : 0
        pyffi.toaster:INFO:
        pyffi.toaster:INFO:Finished.
        """
