import sys

from scripts.cgf import cgftoaster

from tests import test_logger


def call_cgftoaster(*args):
    """Call the NIF cli module"""
    oldargv = sys.argv[:]
    # -j1 to disable multithreading (makes various things impossible)
    sys.argv = ["cgftoaster.py", "-j1"] + list(args)
    toaster = cgftoaster.CgfToaster()
    toaster.logger = test_logger
    toaster.cli()
    sys.argv = oldargv
    return toaster
