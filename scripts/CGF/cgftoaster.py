#!/usr/bin/python

"""A script for casting spells on cgf files. This script is essentially
a cgf specific wrapper around L{PyFFI.Spells.toaster}."""

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

import logging
import sys

import PyFFI.Spells
import PyFFI.Spells.CGF
import PyFFI.Formats.CGF
import PyFFI.Spells.check

# XXX do away with these when converting to new style spells
import PyFFI.Spells.CGF.checktangentspace
import PyFFI.Spells.CGF.checkvcols
import PyFFI.Spells.CGF.dump
import PyFFI.Spells.CGF.readoverwrite
import PyFFI.Spells.CGF.readwrite

class CgfToaster(PyFFI.Spells.CGF.CgfToaster):
    """Class for toasting cgf files, using any of the available spells."""
    SPELLS = [
        PyFFI.Spells.check.SpellRead,
        PyFFI.Spells.CGF.checktangentspace,
        PyFFI.Spells.CGF.checkvcols,
        PyFFI.Spells.CGF.dump,
        PyFFI.Spells.CGF.readoverwrite,
        PyFFI.Spells.CGF.readwrite]
    ALIASDICT = {
        "read": "check_read",
        "readwrite": "check_readwrite"}
    EXAMPLES = """* check if PyFFI can read all files in current directory:

    python cgftoaster.py read .

* same as above, but also find out profile information on reading cgf
  files:

    python -m cProfile -s cumulative -o profile_read.txt cgftoaster.py read .

* find out time spent on a particular test:

    python -m cProfile -s cumulative cgftoaster.py dump"""

# if script is called...
if __name__ == "__main__":
    # set up logger
    logger = logging.getLogger("pyffi")
    logger.setLevel(logging.DEBUG)
    loghandler = logging.StreamHandler(sys.stdout)
    loghandler.setLevel(logging.DEBUG)
    logformatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
    loghandler.setFormatter(logformatter)
    logger.addHandler(loghandler)
    # call toaster
    CgfToaster().cli()
