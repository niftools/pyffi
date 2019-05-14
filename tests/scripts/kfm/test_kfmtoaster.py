"""Tests for the kfmtoaster script"""

from nose.tools import raises

from tests.scripts.kfm import call_kfmtoaster

kfm_dir = "tests/spells/kfm/files/"


@raises(SystemExit)  # --help uses sys.exit()
def test_help():
    """Tests spell help"""
    call_kfmtoaster("--raise", "--help")


def test_examples():
    """Tests example"""
    call_kfmtoaster("--raise", "--examples")


def test_spells():
    """Tests spells"""
    call_kfmtoaster("--raise", "--spells")
    """
    check_read
    check_readwrite
    dump
    """


@raises(ValueError)
def test_raise():
    """Test exception raised on invalid kfm"""
    call_kfmtoaster("--raise", "check_read", kfm_dir + "invalid.kfm")

    """
    pyffi:testlogger:INFO:=== tests/spells/kfm/files/invalid.kfm ===
    pyffi:testlogger:ERROR:FAILED ON tests/spells/kfm/files/invalid.kfm - with the follow exception
    pyffi:testlogger:ERROR:EXPT MSG : Not a KFM file.
    pyffi:testlogger:ERROR:If you were running a spell that came with PyFFI
    pyffi:testlogger:ERROR:Please report this issue - https://github.com/niftools/pyffi/issues
    pyffi:testlogger:INFO:=== tests/spells/kfm/files/test.kfm ===
    pyffi:testlogger:INFO:  --- check_readwrite ---
    pyffi:testlogger:INFO:  writing to temporary file
    pyffi:testlogger:INFO:Finished.
    """


def test_read_write():
    """Test basic read kfm"""
    test_file = kfm_dir + "test.kfm"
    call_kfmtoaster("--raise", "check_readwrite", test_file)
    """
    pyffi.toaster:INFO:=== tests/spells/kfm/files.kfm ===
    pyffi.toaster:INFO:  --- check_readwrite ---
    pyffi.toaster:INFO:    writing to temporary file
    pyffi.toaster:INFO:      comparing file sizes
    pyffi.toaster:INFO:      original size: 166
    pyffi.toaster:INFO:      written size:  168
    pyffi.toaster:INFO:      padding:       2
    pyffi.toaster:INFO:Finished.
    """


def test_dump():
    test_file = kfm_dir + "test.kfm"
    call_kfmtoaster("--raise", "dump", test_file)
    """
    pyffi:testlogger:INFO:=== tests/spells/kfm/files/test.kfm ===
    pyffi:testlogger:INFO:  --- dump ---
    pyffi:testlogger:INFO:    <pyffi.formats.kfm.KfmFormat.Data object at ------->
    pyffi:testlogger:INFO:Finished.
    """
