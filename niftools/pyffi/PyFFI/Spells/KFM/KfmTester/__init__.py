# a script for running hacking, surgery, and validation tests
#
# For validate and surgery tests, exceptions during read will be raised.
# For hacking tests, exceptions during read will be passed; these are intended
# to hack.
# Unlike validate tests, surgery tests modify the original kfm file.
#
# These three functions in the tester script are called:
#    testFile(stream, version, user_version, ...)
#                     - will be called on every kfm
# Not all of these three functions need to be present.

import sys, os
from optparse import OptionParser

from PyFFI.Formats.KFM import KfmFormat

# useful as testFile which simply writes back the file
# but restores the file if the write fails
def testFileOverwrite(stream,
                      version = None, user_version = None,
                      header = None, animations = None, footer = None,
                      **args):
    stream.seek(0)
    backup = stream.read(-1)
    stream.seek(0)
    if args.get('verbose'):
        print "writing %s..."%stream.name
    try:
        KfmFormat.write(
            stream, version = version,
            header = header, animations = animations, footer = footer)
    except: # not just StandardError, also CTRL-C
        print "write failed!!! attempt to restore original file..."
        stream.seek(0)
        stream.write(backup)
        stream.truncate()
        raise
    stream.truncate()

# test all files using testBlock, testRoot, and testFile functions
def testPath(top, testFile = None, raisereaderror = False, mode = 'rb', raisetesterror = True, **args):
    verbose = args.get('verbose', 1)
    for stream, version, user_version, header, animations, footer in KfmFormat.walkFile(top, raisereaderror = raisereaderror, verbose = min(1, verbose), mode = mode):
        # run tests
        try:
            if testFile:
                testFile(
                    stream, version = version, user_version = user_version,
                    header = header, animations = animations, footer = footer,
                    **args)
        except StandardError:
            print """
*** TEST FAILED ON %-51s ***
*** If you were running a script that came with PyFFI, then            ***
*** please report this as a bug (include nif file name or nif file) on ***
*** http://sourceforge.net/tracker/?group_id=149157                    ***
"""%stream.name
            if raisetesterror:
                raise

