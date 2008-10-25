#!/usr/bin/python

"""A script for casting spells on nif files. This script is essentially
a nif specific wrapper around L{PyFFI.Spells.toaster}."""

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

#from PyFFI.Spells import toaster
from PyFFI.Formats.NIF import NifFormat
import PyFFI.Spells.NIF

def main():
    examples = """* check if PyFFI can read all files in current directory
  (python version of nifskope's xml checker):

    python niftoaster.py read .

* optimize all nif files a directory tree, recursively

    python niftoaster.py optimize /path/to/your/nifs/

* print texture information of all nif files a directory tree, recursively

    python niftoaster.py texdump /path/to/your/nifs/

* update/generate mopps of all nif files a directory tree, recursively

    python niftoaster.py updatemopp /path/to/your/nifs/

* update/generate skin partitions of all nif files a directory tree,
recursively, for Freedom Force vs. The 3rd Reich

    python niftoaster.py ffvt3rskinpartition /path/to/your/nifs/

* run the profiler on PyFFI while reading nif files:

    python -m cProfile -s cumulative -o profile_read.txt niftoaster.py read .

* find out time spent on a particular test:

    python -m cProfile -s cumulative niftoaster.py tristrip

* merge skeleton roots and rest positions for all files in current directory:

    python niftoaster.py mergeskelandrestpos .

* scale all files in c:\\zoo2 by a factor 100 - useful to
  visualize nif files from games such as Zoo Tycoon 2 that are otherwise too
  small to show up properly in nifskope:

    python niftoaster.py -a 100 scale "c:\\zoo2"
"""

#    toaster(format=NifFormat, formatspellsmodule=PyFFI.Spells.NIF,
#            examples=examples)
    PyFFI.Spells.NIF.NifToaster().cli()

# if script is called...
if __name__ == "__main__":
    main()

