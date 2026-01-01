import sys

from scripts.nif import niftoaster


def call_niftoaster(*args):
    """Call the NIF cli module"""
    oldargv = sys.argv[:]
    # -j1 to disable multithreading (makes various things impossible)
    sys.argv = ["niftoaster.py", "-j1"] + list(args)
    toaster = niftoaster.NifToaster()
    toaster.cli()
    sys.argv = oldargv
    return toaster
