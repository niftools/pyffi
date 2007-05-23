# a script for running hacking & validation tests (based on wz's NifTester)

import sys, os

from NifFormat.NifFormat import NifFormat

# useful as onreaderror parameter
def raise_exception(e):
    raise e

# useful as onreaderror parameter
def pass_exception(e):
    pass

# test all files using testBlock and testRoot functions
def testPath(top, testBlock, testRoot, testFile, onreaderror = None):
    for version, user_version, f, root_blocks in NifFormat.walkFile(top, onerror = onreaderror, verbose = 1):
        if testBlock:
            for root in root_blocks:
                for block in root.tree():
                    testBlock(block, verbose = 1)
        if testRoot:
            for root in root_blocks:
                testRoot(root, verbose = 1)
        if testFile:
            testFile(version, user_version, f, root_blocks, verbose = 1)

# if script is called...
if __name__ == "__main__":
    if not len(sys.argv) in [2, 3]:
        print """
Run arbitrary tests on files by scriptable testers.
---
Syntax: NifTester.py <tester> [<file> | <dir>]
---
Usage:  Specify a nif file or folder as first argument.
        NifTester will look for a file called "test/hacking/<tester>.py" or
        "test/validate/<tester>.py" and use it for testing the specified
        file, or all nif files in the specified folder.
        If no file or folder is specified, the current directory is
        assumed.

        For validate tests, exceptions during read will be raised.
        For hacking tests, exceptions during read will be passed.

        These three functions in the tester script are called:
          testBlock(block) - will be called on every block in the nif
          testRoot(root)   - will be called on every root block of the nif
          testFile(version, user_version, f, roots)
                           - will be called on every nif
        Not all of them need to be present.

        Examples:

        * check if the library can read all files (python version of
          nifskope's xml checker):

            python NifTester.py read

        * same as above, but also find out profile information on reading nif
          files:

            python -m cProfile -s cumulative NifTester.py read

        * find out time spent on a particular test:

            python -m cProfile -s cumulative NifTester.py skindatacheck | grep skindatacheck

"""
        sys.exit(1)

    test_str = sys.argv[1]
    if len(sys.argv) >= 3:
        top = sys.argv[2]
    else:
        top = '.'

    try:
        testers = __import__('testers.hacking.' + test_str)
        test = getattr(testers.hacking, test_str)
        onreaderror = pass_exception
    except ImportError:
        try:
            testers = __import__('testers.validate.' + test_str)
            test = getattr(testers.validate, test_str)
            onreaderror = raise_exception
        except ImportError:
            print "Tester '%s' was not found!" % test_str
            sys.exit(1)

    testBlock = getattr(test, 'testBlock', None)
    testRoot = getattr(test, 'testRoot', None)
    testFile = getattr(test, 'testFile', None)

    testPath(top, testBlock, testRoot, testFile, onreaderror)
