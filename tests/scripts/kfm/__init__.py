import sys

from scripts.kfm import kfmtoaster

from tests import test_logger


def call_kfmtoaster(*args):
    """Call the KFM cli module"""
    oldargv = sys.argv[:]
    # -j1 to disable multithreading (makes various things impossible)
    sys.argv = ["kfmtoaster.py", "-j1"] + list(args)
    toaster = kfmtoaster.KfmToaster()
    toaster.logger = test_logger
    toaster.cli()
    sys.argv = oldargv
    return toaster
