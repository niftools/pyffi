"""Tests for the get/setbonepriorities spells."""

import shutil
import importlib.resources
from pathlib import Path

import tests.spells.kf
from pyffi.formats.nif import NifFormat
from tests.scripts.nif import call_niftoaster

class TestGetSetBonePrioritiesOblivion:

    file_name = "test_controllersequence.kf"
    txt_name = "test_controllersequence_bonepriorities.txt"

    @staticmethod
    def check_priorities(path, priorities):
        """helper function to check priorities"""
        data = NifFormat.Data()
        with path.open("rb") as stream:
            data.read(stream)
        assert len(data.roots) == 1 
        seq = data.roots[0]
        assert isinstance(seq, NifFormat.NiControllerSequence)
        assert [block.priority for block in seq.controlled_blocks] == priorities

    def test_check_get_set_bonepriorities(self, tmp_path):
        kf_file = tmp_path / self.file_name
        prefixed_kf_file = tmp_path / ("_" + self.file_name)
        txt_file = tmp_path / self.txt_name

        with importlib.resources.path(tests.spells.kf, self.file_name) as original_kf_file:
            shutil.copy(original_kf_file, kf_file)

        self.check_priorities(kf_file, [27, 27, 75])
        toaster = call_niftoaster("--raise", "modify_getbonepriorities", str(kf_file))

        assert list(map(Path, toaster.files_done)) == [kf_file]
        assert txt_file.read_bytes() == b'[TestAction]\r\nBip01=27\r\nBip01 Pelvis=27\r\nBip01 Spine=75\r\n'

        with txt_file.open("wb") as stream:
            stream.write(b"[TestAction]\n")
            stream.write(b"Bip01=33\n")
            stream.write(b"Bip01 Pelvis=29\n")
            stream.write(b"Bip01 Spine=42\n")
        toaster = call_niftoaster("--raise", "modify_setbonepriorities", "--prefix=_", str(kf_file))

        assert list(map(Path, toaster.files_done)) == [kf_file]
        self.check_priorities(prefixed_kf_file, [33, 29, 42])

        # test crlf write
        with txt_file.open("wb") as stream:
            stream.write(b"[TestAction]\r\n")
            stream.write(b"Bip01=38\r\n")
            stream.write(b"Bip01 Pelvis=22\r\n")
            stream.write(b"Bip01 Spine=47\r\n")
        toaster = call_niftoaster("--raise", "modify_setbonepriorities", "--prefix=_", str(kf_file))

        assert list(map(Path, toaster.files_done)) == [kf_file]
        self.check_priorities(prefixed_kf_file, [38, 22, 47])


class TestGetSetBonePrioritiesFallout3(TestGetSetBonePrioritiesOblivion):
    file_name = "test_controllersequence_fo3.kf"
    txt_name = "test_controllersequence_fo3_bonepriorities.txt"
