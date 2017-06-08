"""Tests for the get/setbonepriorities spells."""

import codecs
import os.path

import tempfile
import os
import shutil

import nose.tools

from pyffi.formats.nif import NifFormat
from tests.scripts.nif import call_niftoaster

from os.path import dirname
dir_path = __file__
for i in range(1):  # recurse up to root repo dir
    dir_path = dirname(dir_path)
test_root = dir_path
input_files = os.path.join(test_root, 'spells', 'kf').replace("\\", "/")

class TestGetSetBonePrioritiesOblivion:

    out = None
    file_name = "test_controllersequence.kf"
    txt_name = "test_controllersequence_bonepriorities.txt"

    def setup(self):
        self.out = tempfile.mkdtemp()
        self.kffile = os.path.join(test_root, self.file_name)
        self.kffile2 = os.path.join(test_root, "_" + self.file_name)
        self.txtfile = os.path.join(test_root, self.txt_name)


    def teardown(self):
        shutil.rmtree(self.out)

    @staticmethod
    def check_priorities(filename, priorities):
        """helper function to check priorities"""
        data = NifFormat.Data()
        with open(filename, "rb") as stream:
            data.read(stream)
        nose.tools.assert_equal(len(data.roots), 1) 
        seq = data.roots[0]
        nose.tools.assert_is_instance(seq, NifFormat.NiControllerSequence)
        nose.tools.assert_list_equal(
            [block.priority for block in seq.controlled_blocks], priorities)

    def test_check_get_set_bonepriorities(self):
        TestGetSetBonePrioritiesOblivion.check_priorities(self.kffile, [27, 27, 75])
        toaster = call_niftoaster("--raise", "modify_getbonepriorities", self.kffile)
        nose.tools.assert_equal(list(toaster.files_done), [self.kffile])
        nose.tools.assert_true(os.path.exists(self.txtfile))
        with codecs.open(self.txtfile, "rb", encoding="ascii") as stream:
            contents = stream.read()
            nose.tools.assert_equal(contents,'[TestAction]\r\nBip01=27\r\nBip01 Pelvis=27\r\nBip01 Spine=75\r\n')
        with codecs.open(self.txtfile, "wb", encoding="ascii") as stream:
            stream.write("[TestAction]\n")
            stream.write("Bip01=33\n")
            stream.write("Bip01 Pelvis=29\n")
            stream.write("Bip01 Spine=42\n") # .replace('\r\n', '\n')) # replace probably not needed; just in case
        toaster = call_niftoaster("--raise", "modify_setbonepriorities", "--prefix=_", self.kffile)
        nose.tools.assert_equal(list(toaster.files_done), [self.kffile])
        self.check_priorities(self.kffile2, [33, 29, 42])
        # test crlf write
        with codecs.open(self.txtfile, "wb", encoding="ascii") as stream:
            stream.write("[TestAction]\n")
            stream.write("Bip01=38\n")
            stream.write("Bip01 Pelvis=22\n")
            stream.write("Bip01 Spine=47\n")
        toaster = call_niftoaster("--raise", "modify_setbonepriorities", "--prefix=_", self.kffile)
        nose.tools.assert_equal(list(toaster.files_done), [self.kffile])
        self.check_priorities(self.kffile2, [38, 22, 47])
        os.remove(self.txtfile)
        os.remove(self.kffile2)


class TestGetSetBonePrioritiesFallout3(TestGetSetBonePrioritiesOblivion):
    file_name = "test_controllersequence_fo3.kf"
    txt_name = "test_controllersequence_fo3_bonepriorities.txt"
