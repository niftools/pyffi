"""Tests for the get/setbonepriorities spells."""

import codecs
import os
import os.path
import nose.tools
# if nose refuses to show the diffs, uncomment the next line
#nose.tools.assert_equal.im_self.maxDiff = None

from pyffi.formats.nif import NifFormat
from tests.test_nif import call_niftoaster

class TestGetSetBonePrioritiesOblivion:
    kffile = "tests/test_nif/test_controllersequence.kf"
    kffile2 = "tests/test_nif/_test_controllersequence.kf"
    txtfile = "tests/test_nif/test_controllersequence_bonepriorities.txt"

    def check_priorities(self, filename, priorities):
        # helper function to check priorities
        data = NifFormat.Data()
        with open(filename, "rb") as stream:
            data.read(stream)
        nose.tools.assert_equal(len(data.roots), 1) 
        seq = data.roots[0]
        nose.tools.assert_is_instance(seq, NifFormat.NiControllerSequence)
        nose.tools.assert_list_equal(
            [block.priority for block in seq.controlled_blocks], priorities)

    def test_check_get_set_bonepriorities(self):
        self.check_priorities(self.kffile, [27, 27, 75])
        toaster = call_niftoaster("modify_getbonepriorities", self.kffile)
        nose.tools.assert_equal(list(toaster.files_done), [self.kffile])
        nose.tools.assert_true(os.path.exists(self.txtfile))
        with codecs.open(self.txtfile, "rb", encoding="ascii") as stream:
            nose.tools.assert_equal(stream.read(), """\
[TestAction]
Bip01=27
Bip01 Pelvis=27
Bip01 Spine=75
""".replace('\n', '\r\n'))
        with codecs.open(self.txtfile, "wb", encoding="ascii") as stream:
            stream.write("""\
[TestAction]
Bip01=33
Bip01 Pelvis=29
Bip01 Spine=42
""".replace('\r\n', '\n')) # replace probably not needed; just in case
        toaster = call_niftoaster("modify_setbonepriorities", "--prefix=_", self.kffile)
        nose.tools.assert_equal(list(toaster.files_done), [self.kffile])
        self.check_priorities(self.kffile2, [33, 29, 42])
        # test crlf write
        with codecs.open(self.txtfile, "wb", encoding="ascii") as stream:
            stream.write("""\
[TestAction]
Bip01=38
Bip01 Pelvis=22
Bip01 Spine=47
""".replace('\n', '\r\n'))
        toaster = call_niftoaster("modify_setbonepriorities", "--prefix=_", self.kffile)
        nose.tools.assert_equal(list(toaster.files_done), [self.kffile])
        self.check_priorities(self.kffile2, [38, 22, 47])
        os.remove(self.txtfile)
        os.remove(self.kffile2)

class TestGetSetBonePrioritiesFallout3(TestGetSetBonePrioritiesOblivion):
    kffile = "tests/test_nif/test_controllersequence_fo3.kf"
    kffile2 = "tests/test_nif/_test_controllersequence_fo3.kf"
    txtfile = "tests/test_nif/test_controllersequence_fo3_bonepriorities.txt"
