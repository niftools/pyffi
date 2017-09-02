import imp
import os.path
import sys

from tests import test_logger

from os.path import dirname
dir_path = __file__
for i in range(4):  # recurse up to root repo dir
    dir_path = dirname(dir_path)
repo_root = dir_path

niftoaster = imp.load_module("niftoaster", *imp.find_module("niftoaster", [os.path.join(repo_root, "scripts", "nif")]))


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
