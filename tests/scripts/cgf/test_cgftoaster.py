"""Tests for the cgftoaster script"""
from nose.tools import raises
from tests.scripts.cgf import call_cgftoaster

cfg_dir = "tests/spells/cgf/files/"


@raises(SystemExit)  # --help uses sys.exit()
def test_help():
    """Tests spell help"""
    call_cgftoaster("--raise", "--help")


def test_examples():
    """Tests example"""
    call_cgftoaster("--raise", "--examples")


def test_spells():
    """Tests spells"""
    call_cgftoaster("--raise", "--spells")

    """
    check_read
    check_readwrite
    check_tangentspace
    check_vcols
    dump
    """


@raises(ValueError)
def test_raise():
    """Test check_read and check_readwrite spells"""
    call_cgftoaster("--raise", "check_read", cfg_dir)

    """
    pyffi.toaster:INFO:=== tests/formats/cgf/invalid.cgf ===
    pyffi.toaster:ERROR:FAILED ON tests/formats/cgf/invalid.cgf - with the follow exception
    pyffi.toaster:ERROR:EXPT MSG : Invalid signature (got 'b'INVALI'' instead of 'CryTek' or 'NCAion')
    pyffi.toaster:ERROR:If you were running a spell that came with PyFFI
    pyffi.toaster:ERROR:Please report this issue - https://github.com/niftools/pyffi/issues
    pyffi.toaster:INFO:=== tests/formats/cgf/monkey.cgf ===
    pyffi.toaster:INFO:  --- check_read ---
    pyffi.toaster:INFO:=== tests/formats/cgf/test.cgf ===
    pyffi.toaster:INFO:  --- check_read ---
    pyffi.toaster:INFO:=== tests/formats/cgf/vcols.cgf ===
    pyffi.toaster:INFO:  --- check_read ---
    pyffi.toaster:INFO:Finished.
    """


def test_read_write():
    test_file = cfg_dir + "test.cgf"
    call_cgftoaster("--raise", "check_readwrite", test_file)
    """
    pyffi.toaster:INFO:=== tests/formats/cgf/test.cgf ===
    pyffi.toaster:INFO:  --- check_readwrite ---
    pyffi.toaster:INFO:    writing to temporary file
    pyffi.toaster:INFO:      comparing file sizes
    pyffi.toaster:INFO:      original size: 166
    pyffi.toaster:INFO:      written size:  168
    pyffi.toaster:INFO:      padding:       2
    pyffi.toaster:INFO:Finished.
    """
