#!/usr/bin/python
# a script for updating ffvt3r skin partitions

def testBlock(block, verbose):
    # does it apply on this block?
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    # does this block have a skin?
    if not block.skinInstance: return

    print "updating skin partition of block '%s'"%block.name
    block._validateSkin()
    skininst = block.skinInstance
    skinpart = skininst.skinPartition
    if not skinpart:
        skinpart = skininst.data.skinPartition

    # use ffvt3r settings
    block.updateSkinPartition(minbonesperpartition = 4, maxbonesperpartition = 4, maxbonespervertex = 4, stripify = False, verbose = verbose)

def testFile(version, user_version, f, roots, verbose, arg = None):
    f.seek(0)
    NifFormat.write(version, user_version, f, roots)
    f.truncate()

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

def main():
    # parse options and positional arguments
    usage = "%prog [options] <file>|<folder>"
    description="""Update all skin partitions of file <file> or of all nif 
files in folder <folder> for Freedom Force vs. the 3rd Reich.
This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup before running this script."""
    parser = OptionParser(usage, version="%prog $Rev$", description=description)
    parser.add_option("-v", "--verbose", dest="verbose",
                      type="int",
                      metavar="VERBOSE",
                      default=1,
                      help="verbosity level: 0, 1, or 2 [default: %default]")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments (one required)")

    # get top folder/file
    top = args[0]

    # run tester
    testPath(top, testBlock, None, testFile, raise_exception, "r+b", verbose=options.verbose)

# if script is called...
if __name__ == "__main__":
    main()
