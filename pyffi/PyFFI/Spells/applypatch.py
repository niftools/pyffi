"""This spell simply applies a binary patch."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
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
# --------------------------------------------------------------------------

import subprocess

import PyFFI.Utils.BSDiff

# TODO: ditch the .patched suffix and set flag that this spell overwrites files
#__readonly__ = False

def testFile(*walkresult, **kwargs):
    """Apply patch.

    @param walkresult: Tuple with result from walkFile.
    @type walkresult: tuple
    @param kwargs: Extra keyword arguments.
    @type kwargs: dict
    """
    patchcmd = kwargs.get("patchcmd")
    # first argument is always the stream, by convention
    oldfile = walkresult[0]
    oldfilename = oldfile.name
    newfilename = oldfilename + ".patched"
    patchfilename = oldfilename + ".patch"
    if not patchcmd:
        patchfile = open(patchfilename, "rb")
        newfile = open(newfilename, "wb")
        try:
            if kwargs.get('verbose'):
                print("  writing %s..." % newfilename)
            #print(walkresult) # DEBUG
            # walkresult[0] is original file
            # stream is patched file (to be written)
            PyFFI.Utils.BSDiff.patch(oldfile, newfile, patchfile)
        finally:
            newfile.close()
            patchfile.close()
    else:
        # close all files before calling external command
        oldfile.close()
        subprocess.call([patchcmd, oldfilename, newfilename, patchfilename])

