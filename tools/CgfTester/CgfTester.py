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

def examples_callback(option, opt, value, parser):
    print """* check if the library can read all files in current directory:

    python CgfTester.py read .

* same as above, but also find out profile information on reading cgf
  files:

    python -m cProfile -s cumulative -o profile_read.txt CgfTester.py read .

* find out time spent on a particular test:

    python -m cProfile -s cumulative CgfTester.py tristrip . | grep tristrip"""
    sys.exit(0)

def tests_callback(option, opt, value, parser):
    import testers
    for category in dir(testers):
        if category[:2] == '__': continue
        print category + ':'
        tests = __import__('testers.' + category)
        tests = getattr(tests, category)
        for test in dir(tests):
            if test[:2] == '__': continue
            print '  ' + test
    sys.exit(0)

def main():
    # parse options and positional arguments
    usage = "%prog [options] <tester> <file>|<folder>"
    description="""Look for a python script "testers/hacking/<tester>.py",
"testers/validate/<tester>.py", or "testers/surgery/<tester>.py"
and use the functions testChunk and testFile therein
for hacking, modifying, or validating <file>, or the files in <folder>."""

    parser = OptionParser(usage, version="%prog $Rev$", description=description)
    parser.add_option("-a", "--arg", dest="arg",
                      type="string",
                      metavar="ARG",
                      help="pass argument ARG to tester")
    parser.add_option("--examples",
                      action="callback", callback=examples_callback,
                      help="show examples of usage and exit")
    parser.add_option("-v", "--verbose", dest="verbose",
                      type="int",
                      metavar="VERBOSE",
                      default=1,
                      help="verbosity level: 0, 1, or 2 [default: %default]")
    parser.add_option("--testers",
                      action="callback", callback=tests_callback,
                      help="list all testers and exit")
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("incorrect number of arguments (two required)")

    # get tester and top folder/file
    test_str = args[0]
    top = args[1]

    try:
        testers = __import__('testers.hacking.' + test_str)
        test = getattr(testers.hacking, test_str)
        onreaderror = pass_exception
        mode = 'rb'
    except ImportError:
        try:
            testers = __import__('testers.validate.' + test_str)
            test = getattr(testers.validate, test_str)
            onreaderror = raise_exception
            mode = 'rb'
        except ImportError:
            try:
                testers = __import__('testers.surgery.' + test_str)
                test = getattr(testers.surgery, test_str)
                onreaderror = raise_exception
                mode = 'r+b'
            except ImportError:
                # either tester was not found, or had an error while importing
                parser.error("tester '%s' not found" % test_str)

    testChunk = getattr(test, 'testChunk', None)
    testFile = getattr(test, 'testFile', None)

    # run tester
    testPath(top, testChunk, testFile, onreaderror, mode, verbose=options.verbose, arg=options.arg)

# if script is called...
if __name__ == "__main__":
    main()
