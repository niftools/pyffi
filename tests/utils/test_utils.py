"""Tests for pyffi.utils module."""

from pyffi.utils import unique_map, hex_dump
import nose.tools


def test_hex_dump():
    """Test output of hex_dump function"""
    from tests import test_logger
    from tempfile import TemporaryFile
    f = TemporaryFile()
    if f.write('abcdefg\\x0a'.encode("ascii")):
        pass
    if f.seek(2):
        pass  # ignore result for py3k
    contents = hex_dump(f, 1)
    test_logger.debug(contents)
    nose.tools.assert_in("00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F", contents)
    nose.tools.assert_in("0x00000000  61 62>63 64 65 66 67 5C 78 30 61                |abcdefg\\x0a     |", contents)


def test_unique_map():
    """Test unique map generator"""
    nose.tools.assert_equals(unique_map([]), ([], []))
    nose.tools.assert_equals(unique_map([3, 2, 6, None, 1]), ([0, 1, 2, None, 3], [0, 1, 2, 4]))
    nose.tools.assert_equals(unique_map([3, 1, 6, 1]), ([0, 1, 2, 1], [0, 1, 2]))
    nose.tools.assert_equals(unique_map([3, 1, 6, 1, 2, 2, 9, 3, 2]), ([0, 1, 2, 1, 3, 3, 4, 0, 3], [0, 1, 2, 4, 6]))
