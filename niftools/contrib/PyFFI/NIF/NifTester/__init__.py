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
#    testFile(stream, version, user_version, roots)
#                     - will be called on every nif
# Not all of these three functions need to be present.

import sys, os
from optparse import OptionParser

from PyFFI.Formats.NIF import NifFormat

# useful as testFile which simply writes back the file
# but restores the file if the write fails
def testFileOverwrite(stream,
                      version = None, user_version = None, roots = None,
                      **args):
    stream.seek(0)
    backup = stream.read(-1)
    stream.seek(0)
    if args.get('verbose'):
        print "writing %s..."%stream.name
    try:
        NifFormat.write(
            stream,
            version = version, user_version = user_version, roots = roots)
    except: # not just StandardError, also CTRL-C
        print "write failed!!! attempt to restore original file..."
        stream.seek(0)
        stream.write(backup)
        stream.truncate()
        raise
    stream.truncate()

# test all files using testBlock, testRoot, and testFile functions
def testPath(top, testBlock = None, testRoot = None, testFile = None, raisereaderror = False, mode = 'rb', raisetesterror = True, **args):
    verbose = args.get('verbose', 1)
    for stream, version, user_version, root_blocks in NifFormat.walkFile(top, raisereaderror = raisereaderror, verbose = min(1, verbose), mode = mode):
        # find blocks beforehand as tree hierarchy may change after each
        # test (especially for surgery tests)
        for root in root_blocks:
            blockslist = [[block for block in root.tree(unique = True)] for root in root_blocks]
        # run tests
        try:
            if testRoot:
                for root in root_blocks:
                    testRoot(root, **args)
            if testBlock:
                for blocks in blockslist:
                    for block in blocks:
                        testBlock(block, **args)
            if testFile:
                testFile(
                    stream,
                    version = version, user_version = user_version,
                    roots = root_blocks, **args)
        except StandardError:
            print """
*** TEST FAILED ON %-51s ***
*** If you were running a script that came with PyFFI, then            ***
*** please report this as a bug (include nif file name or nif file) on ***
*** http://sourceforge.net/tracker/?group_id=149157                    ***
"""%stream.name
            if raisetesterror:
                raise

