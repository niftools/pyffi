#!/usr/bin/python

"""
A script for updating ffvt3r skin partitions
"""

import NifTester

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
    block.updateSkinPartition(maxbonesperpartition = 4, maxbonespervertex = 4, stripify = False, verbose = verbose, padbones = True)

def testFile(version, user_version, f, roots, verbose, arg = None):
    f.seek(0)
    NifFormat.write(version, user_version, f, roots)
    f.truncate()

import sys, os
from optparse import OptionParser

from PyFFI.NIF import NifFormat

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
    NifTester.testPath(top, testBlock, None, testFile, NifTester.raise_exception, "r+b", verbose=options.verbose)

# if script is called...
if __name__ == "__main__":
    main()
