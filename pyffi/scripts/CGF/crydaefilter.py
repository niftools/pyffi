#!/usr/bin/python

"""Parses a collada file and outputs a similar collada file which can be used
with Crytek's resource compiler."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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
#    * Neither the name of the Python File Format Interface
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

import optparse

import PyFFI.Utils.CryDaeFilter

def main():
    """Parse options and run dae convertor."""
    usage = "%prog [options] <infile> <outfile>"
    description = __doc__
    parser = optparse.OptionParser(
        usage,
        version="%%prog (PyFFI %s)" % PyFFI.__version__,
        description=description)
    parser.add_option("-v", "--verbose", dest="verbose",
                      type="int",
                      metavar="VERBOSE",
                      help="verbosity level [default: %default]")
    parser.add_option("-p", "--pause", dest="pause",
                      action="store_true",
                      help="pause when done")
    parser.set_defaults(pause=False, verbose=1)
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("incorrect number of arguments")

    infile = open(args[0], "r")
    try:
        # check that input is not yet a CryEngine dae file!
        if infile.read(-1).find("CryExportNode") != -1:
            raise RuntimeError("%s is already a CryEngine dae file")
        infile.seek(0)
        # open output file
        outfile = open(args[1], "w")
        # convert the file
        try:
            if options.verbose:
                print("converting %s to CryEngine dae file %s..."
                      % (infile.name, outfile.name))
            PyFFI.Utils.CryDaeFilter.convert(infile, outfile,
                                             verbose=options.verbose)
        finally:
            outfile.close()
    finally:
        infile.close()

    # signal the end
    if options.verbose:
        finalmessage = "Finished."
    else:
        # writing to stdout, so don't print an extra message
        finalmessage = ""
    # pause if needed
    if options.pause:
        raw_input(finalmessage)
    else:
        print(finalmessage)

if __name__ == '__main__':
    main()
