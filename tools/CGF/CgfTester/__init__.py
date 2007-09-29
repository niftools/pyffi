# a script for running hacking, surgery, and validation tests (based on wz's NifTester)
#
# For validate and surgery tests, exceptions during read will be raised.
# For hacking tests, exceptions during read will be passed; these are intended
# for file format decoding.
# Unlike validate tests, surgery tests modify the original cgf file.
#
# These three functions in the tester script are called:
#    testChunk(block) - will be called on every chunk in the cgf
#    testFile(filetype, fileversion, f, chunks, versions)
#                     - will be called on every cgf
# Not all of these three functions need to be present.

import sys, os
from optparse import OptionParser

from PyFFI.CGF import CgfFormat

# useful as onreaderror parameter
def raise_exception(e):
    raise e

# useful as onreaderror parameter
def pass_exception(e):
    pass

# test all files using testChunk and testFile functions
def testPath(top, testChunk, testFile, onreaderror = None, mode = 'rb', verbose = None, arg = None):
    kwargs = {}
    kwargs['verbose'] = verbose if verbose != None else 0
    if arg != None: kwargs['arg'] = arg
    for filetype, fileversion, f, chunks, versions in CgfFormat.walkFile(top, onerror = onreaderror, verbose = min(1, verbose), mode = mode):
        if testChunk:
            for chunk in chunks:
                testChunk(block, **kwargs)
        if testFile:
            testFile(filetype, fileversion, f, chunks, versions, **kwargs)
