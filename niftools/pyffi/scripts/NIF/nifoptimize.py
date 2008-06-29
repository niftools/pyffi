#!/usr/bin/python

"""A script for optimizing nif files."""

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

from PyFFI.Spells import testPath
from PyFFI.Formats.NIF import NifFormat
import PyFFI.Spells.NIF.optimize

import sys, os
from optparse import OptionParser

def main():
    # parse options and positional arguments
    usage = "%prog [options] <file>|<folder>"
    description="""Optimize nif file <file> or all nif files in folder <folder>.
This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup before running this script."""
    parser = OptionParser(usage, version="%prog $Rev$", description=description)
    parser.add_option("-r", "--raise", dest="raisetesterror",
                      action="store_true",
                      help="raise exception on errors during optimization")
    parser.add_option("-v", "--verbose", dest="verbose",
                      type="int",
                      metavar="VERBOSE",
                      help="verbosity level: 0, 1, or 2 [default: %default]")
    parser.add_option("-p", "--pause", dest="pause",
                      action="store_true",
                      help="pause when done")
    parser.add_option("-x", "--exclude", dest="exclude",
                      action="append",
                      help="exclude given block type from optimization \
(you can exclude multiple block types by specifying this option multiple \
times)")
    parser.set_defaults(raisetesterror = False, verbose = 1, pause = False,
                        exclude = [])
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments (one required)")

    # get top folder/file
    top = args[0]

    # warning
    print("""This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup of your nif files before running this script.
""")
    if not raw_input("Are you sure that you want to proceed? [n/y] ") in ["y", "Y"]:
        if options.pause:
            raw_input("Script aborted by user.")
        else:
            print("Script aborted by user.")
        return

    # run tester
    testPath(
        top, format=NifFormat, formatspellsmodule=PyFFI.Spells.NIF.optimize,
        verbose = options.verbose, raisetesterror = options.raisetesterror,
        exclude = options.exclude)

    if options.pause:
        raw_input("Finished.")

# if script is called...
if __name__ == "__main__":
    main()
