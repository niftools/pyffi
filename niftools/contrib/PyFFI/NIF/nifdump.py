#!/usr/bin/python

"""A script for dumping particular blocks from nifs."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, NIF File Format Library and Tools.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the NIF File Format Library and Tools
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****
# --------------------------------------------------------------------------

import NifTester

############################################################################
# custom functions
############################################################################

def dumpArray(block):
    """Dump an array."""
    text = ""
    if block._count2 == None:
        for i, element in enumerate(list.__iter__(block)):
            if i > 16:
                text += "etc...\n"
                break
            text += "%i: %s\n" % (i, dumpAttr(element))
    else:
        k = 0
        for i, elemlist in enumerate(list.__iter__(block)):
            for j, elem in enumerate(list.__iter__(elemlist)):
                if k > 16:
                    text += "etc...\n"
                    break
                text += "%i, %i: %s\n" % (i, j, dumpAttr(elem))
                k += 1
            if k > 16:
                break
    return text if text else "None"

def dumpBlock(block):
    """Print block without following references."""
    text = '%s instance at 0x%08X\n' % (block.__class__.__name__, id(block))
    for attr in block._filteredAttributeList():
        attr_str_lines = dumpAttr(getattr(block, "_%s_value_" % attr.name)).splitlines()
        if len(attr_str_lines) > 1:
            text += '* %s :\n' % attr.name
            for attr_str in attr_str_lines:
                text += '    %s\n' % attr_str
        else:
            text += '* %s : %s\n' % (attr.name, attr_str_lines[0])
    return text

def dumpAttr(attr):
    if isinstance(attr, (NifFormat.Ref, NifFormat.Ptr)):
        ref = attr.getValue()
        if ref:
            return "<%s instance at 0x%08X>" % (ref.__class__.__name__, id(attr))
        else:
            return "<None>"
    elif isinstance(attr, list):
        return dumpArray(attr)
    elif isinstance(attr, NifFormat.NiObject):
        return dumpBlock(attr)
    else:
        return str(attr)

############################################################################
# testers
############################################################################

# set this variable to True for scripts that need to overwrite of original files
OVERWRITE_FILES = False

def testBlock(block, **args):
    if isinstance(block, getattr(NifFormat, args["blocktype"])):
        print dumpBlock(block)

############################################################################
# main program
############################################################################

import sys, os
from optparse import OptionParser

from PyFFI.NIF import NifFormat

def main():
    # parse options and positional arguments
    usage = "%prog [options] <file>|<folder>"
    description="""A nif script for parsing nif file <file> or all nif files in folder
<folder> and dumping particular blocks."""
    if OVERWRITE_FILES:
        description += """
WARNING:
This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup before running this script."""
    parser = OptionParser(usage, version="%prog $Rev$", description=description)
    parser.add_option("-v", "--verbose", dest="verbose",
                      type="int",
                      metavar="VERBOSE",
                      default=1,
                      help="verbosity level: 0, 1, or 2 [default: %default]")
    parser.add_option("-b", "--blocktype", dest="blocktype",
                      type="string",
                      metavar="BLOCKTYPE",
                      default="NiNode",
                      help="block type [default: %default]")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments (one required)")

    # get top folder/file
    top = args[0]

    # warning
    if OVERWRITE_FILES:
        print """This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup of your nif files before running this script.
"""
        if raw_input("Are you sure that you want to proceed? [n/Y] ") != "Y": return

    # run tester
    mode = "rb" if not OVERWRITE_FILES else "r+b"
    NifTester.testPath(top, testBlock = testBlock, raisereaderror = True, mode = mode, verbose = options.verbose, blocktype = options.blocktype)

# if script is called...
if __name__ == "__main__":
    main()
