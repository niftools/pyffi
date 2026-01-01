import sys

from scripts.nif import niftoaster

from tests import test_logger


def call_niftoaster(*args):
    """Call the NIF cli module"""
    oldargv = sys.argv[:]
    # -j1 to disable multithreading (makes various things impossible)
    sys.argv = ["niftoaster.py", "-j1"] + list(args)
    toaster = niftoaster.NifToaster()
    toaster.logger = test_logger
    toaster.cli()
    sys.argv = oldargv
    return toaster
