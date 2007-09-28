# a script for running hacking, surgery, and validation tests (based on wz's NifTester)
#
# For validate and surgery tests, exceptions during read will be raised.
# For hacking tests, exceptions during read will be passed; these are intended
# to hack .
# Unlike validate tests, surgery tests modify the original nif file.
#
# These three functions in the tester script are called:
#    testBlock(block) - will be called on every block in the nif
#    testRoot(root)   - will be called on every root block of the nif
#    testFile(version, user_version, f, roots)
#                     - will be called on every nif
# Not all of these three functions need to be present.

import sys, os
from optparse import OptionParser

from PyFFI.NIF import NifFormat

# useful as onreaderror parameter
def raise_exception(e):
    raise e

# useful as onreaderror parameter
def pass_exception(e):
    pass

# test all files using testBlock, testRoot, and testFile functions
def testPath(top, testBlock, testRoot, testFile, onreaderror = None, mode = 'rb', verbose = None, arg = None):
    kwargs = {}
    kwargs['verbose'] = verbose if verbose != None else 0
    if arg != None: kwargs['arg'] = arg
    for version, user_version, f, root_blocks in NifFormat.walkFile(top, onerror = onreaderror, verbose = min(1, verbose), mode = mode):
        # find blocks beforehand as tree hierarchy may change after each
        # test (especially for surgery tests)
        for root in root_blocks:
            blockslist = [[block for block in root.tree()] for root in root_blocks]
        # run tests
        if testRoot:
            for root in root_blocks:
                testRoot(root, **kwargs)
        if testBlock:
            for blocks in blockslist:
                for block in blocks:
                    testBlock(block, **kwargs)
        if testFile:
            testFile(version, user_version, f, root_blocks, **kwargs)
