import imp
import os.path
import sys

from tests import test_logger

from os.path import dirname
dir_path = __file__
for i in range(4):  # recurse up to root repo dir
    dir_path = dirname(dir_path)

repo_root = dir_path
kfmtoaster = imp.load_module("kfmtoaster", *imp.find_module("kfmtoaster", [os.path.join(repo_root, "scripts", "kfm")]))


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
