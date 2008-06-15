# a script for running hacking, surgery, and validation tests (based on wz's NifTester)
#
# For validate and surgery tests, exceptions during read will be raised.
# For hacking tests, exceptions during read will be passed; these are intended
# for file format decoding.
# Unlike validate tests, surgery tests modify the original cgf file.
#
# These three functions in the tester script are called:
#    testChunk(chunk) - will be called on every chunk in the cgf
#    testFile(stream, filetype, fileversion, game, chunks, versions)
#                     - will be called on every cgf
# Not all of these three functions need to be present.

import sys, os, gc
from optparse import OptionParser

from PyFFI.CGF import CgfFormat

# useful as testFile which simply writes back the file
# but restores the file if the write fails
def testFileOverwrite(stream,
                      filetype = None, fileversion = None, game = None,
                      chunks = None, versions = None, **kwargs):
    stream.seek(0)
    backup = stream.read(-1)
    stream.seek(0)
    if args.get('verbose'):
        print "writing %s..."%stream.name
    try:
        CgfFormat.write(
            stream,
            filetype = filetype, fileversion = fileversion, game = game,
            chunks = chunks, versions = versions)
    except: # not just StandardError, also CTRL-C
        print "write failed!!! attempt to restore original file..."
        stream.seek(0)
        stream.write(backup)
        stream.truncate()
        raise
    stream.truncate()

# test all files using testChunk and testFile functions
def testPath(top, testChunk, testFile, raisereaderror = False, mode = 'rb', verbose = None, arg = None):
    kwargs = {}
    kwargs['verbose'] = verbose if verbose != None else 0
    if arg != None:
        kwargs['arg'] = arg
    for filetype, fileversion, game, stream, chunks, versions in CgfFormat.walkFile(top, raisereaderror = raisereaderror, verbose = min(1, verbose), mode = mode):
        if testChunk:
            for chunk in chunks:
                testChunk(chunk, **kwargs)
        if testFile:
            testFile(
                stream,
                filetype = filetype, fileversion = fileversion, game = game,
                chunks = chunks, versions = versions, **kwargs)
        # force free memory
        del stream, chunks, versions
        gc.collect()

