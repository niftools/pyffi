from nose.tools import assert_equals

from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase


class TestModifyAllBonePrioritiesNif(BaseNifFileTestCase):
    """Tests for the modify_allbonepriorities spell"""

    def setUp(self):
        super(TestModifyAllBonePrioritiesNif, self).setUp()
        self.src_name = "test_fix_cleanstringpalette.nif"
        super(TestModifyAllBonePrioritiesNif, self).copyFile()
        super(TestModifyAllBonePrioritiesNif, self).readNifData()

        def test_non_interactive_modify_all_bone_priorities(self):
            """Run the spell that modifies the bone prioirities"""

            # check current controller blocks
            assert_equals([block.priority
                           for block in self.data.roots[0].controller.controller_sequences[0].controlled_blocks],
                          [0, 0])
            assert_equals([block.priority
                           for block in self.data.roots[0].controller.controller_sequences[1].controlled_blocks],
                          [0, 0])

            call_niftoaster("--raise", "modify_allbonepriorities", "-a", "50", "--dry-run", "--noninteractive",
                            "--verbose=1", self.dest_file)
            """
            pyffi.toaster:INFO:=== tests/spells/nif/files/test_fix_cleanstringpalette.nif ===
            pyffi.toaster:INFO:  --- modify_allbonepriorities ---
            pyffi.toaster:INFO:    ~~~ NiNode [TestCleanStringPalette] ~~~
            pyffi.toaster:INFO:      ~~~ NiControllerManager [] ~~~
            pyffi.toaster:INFO:        ~~~ NiControllerSequence [Scared] ~~~
            pyffi.toaster:INFO:          b'Test' priority changed to 50
            pyffi.toaster:INFO:          b'Test NonAccum' priority changed to 50
            pyffi.toaster:INFO:        ~~~ NiControllerSequence [Death] ~~~
            pyffi.toaster:INFO:          b'Test' priority changed to 50
            pyffi.toaster:INFO:          b'Test NonAccum' priority changed to 50
            pyffi.toaster:INFO:  writing tests/spells/nif/files..._test_fix_cleanstringpalette.nif
            pyffi.toaster:INFO:Finished.
            """

            assert_equals([block.priority
                           for block in self.data.roots[0].controller.controller_sequences[0].controlled_blocks],
                          [50, 50])
            assert_equals([block.priority
                           for block in self.data.roots[0].controller.controller_sequences[1].controlled_blocks],
                          [50, 50])
