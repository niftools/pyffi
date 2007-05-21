# a script for running hacking & validation tests (based on wz's NifTester)

import sys, os

from NifFormat.NifFormat import NifFormat

def testPath(top, testBlock, testRoot):
    for root_blocks in NifFormat.walk(top, onerror = onreaderror, verbose = 1):
        if testBlock:
            for root in root_blocks:
                for block in root.tree():
                    testBlock(block, verbose = 1)
        if testRoot:
            for root in root_blocks:
                testRoot(root, verbose = 1)

if __name__ == "__main__":
    if not len(sys.argv) in [2, 3]:
        print """
Run arbitrary tests on files by scriptable testers.
---
Syntax: runtest.py <tester> [<file> | <dir>]
---
Usage:  Specify a nif file or folder as first argument.
        runtest will look for a file called "test/hacking/<tester>.py" or
        "test/validate/<tester>.py" and use it for testing the specified
        file, or all nif files in the specified folder.
        If no file or folder is specified, the current directory is
        assumed.

        For validate tests, exceptions during read will be raised.
        For hacking tests, exceptions during read will be passed.

        The tester.py script may contain two functions:
          testBlock(block) - will be called on every block in the nif
          testRoot(root)   - will be called on every root block of the nif
        Not both need to be present.
"""
        sys.exit(1)

    tester_str = sys.argv[1]
    if len(sys.argv) >= 3:
        top = sys.argv[2]
    else:
        top = '.'

    def raise_exception(e):
        raise e

    def pass_exception(e):
        pass

    try:
        test = __import__('test.hacking.' + tester_str)
        tester = getattr(test.hacking, tester_str)
        onreaderror = pass_exception
    except ImportError:
        try:
            test = __import__('test.validate.' + tester_str)
            tester = getattr(test.validate, tester_str)
            onreaderror = raise_exception
        except ImportError:
            print "Tester '%s' was not found!" % tester_str
            sys.exit(1)

    testBlock = getattr(tester, 'testBlock', None)
    testRoot = getattr(tester, 'testRoot', None)

    testPath(top, testBlock, testRoot)
