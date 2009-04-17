#!/usr/bin/python

"""A script for casting spells on nif files. This script is essentially
a nif specific wrapper around L{PyFFI.Spells.Toaster}."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, NIF File Format Library and Tools.
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

import logging
import sys

from PyFFI.Formats.NIF import NifFormat
import PyFFI.Spells.check
import PyFFI.Spells.NIF
import PyFFI.Spells.NIF.check
import PyFFI.Spells.NIF.dump
import PyFFI.Spells.NIF.fix
import PyFFI.Spells.NIF.optimize
from PyFFI.Spells.NIF import \
    hackmultiskelroot, \
    hackskinrestpose, \
    mergeskelandrestpos, \
    optimize_split, \
    scale, \
    updatecenterradius, \
    updatemopp, \
    updateskinpartition

class NifToaster(PyFFI.Spells.NIF.NifToaster):
    """Class for toasting nif files, using any of the available spells."""
    SPELLS = [
        PyFFI.Spells.check.SpellRead,
        PyFFI.Spells.NIF.check.SpellReadWrite,
        PyFFI.Spells.NIF.check.SpellNodeNamesByFlag,
        PyFFI.Spells.NIF.check.SpellCompareSkinData,
        PyFFI.Spells.NIF.check.SpellCheckBhkBodyCenter,
        PyFFI.Spells.NIF.check.SpellCheckCenterRadius,
        PyFFI.Spells.NIF.check.SpellCheckConvexVerticesShape,
        PyFFI.Spells.NIF.check.SpellCheckMopp,
        PyFFI.Spells.NIF.check.SpellCheckSkinCenterRadius,
        PyFFI.Spells.NIF.check.SpellCheckTangentSpace,
        PyFFI.Spells.NIF.check.SpellCheckTriStrip,
        PyFFI.Spells.NIF.dump.SpellDumpAll,
        PyFFI.Spells.NIF.dump.SpellDumpTex,
        PyFFI.Spells.NIF.dump.SpellHtmlReport,
        PyFFI.Spells.NIF.dump.SpellExportPixelData,
        PyFFI.Spells.NIF.fix.SpellAddTangentSpace,
        PyFFI.Spells.NIF.fix.SpellClampMaterialAlpha,
        PyFFI.Spells.NIF.fix.SpellDelTangentSpace,
        PyFFI.Spells.NIF.fix.SpellDetachHavokTriStripsData,
        PyFFI.Spells.NIF.fix.SpellDisableParallax,
        PyFFI.Spells.NIF.fix.SpellFFVT3RSkinPartition,
        PyFFI.Spells.NIF.fix.SpellFixTexturePath,
        PyFFI.Spells.NIF.fix.SpellSendGeometriesToBindPosition,
        PyFFI.Spells.NIF.fix.SpellSendBonesToBindPosition,
        PyFFI.Spells.NIF.fix.SpellStrip,
        hackmultiskelroot,
        hackskinrestpose,
        mergeskelandrestpos,
        PyFFI.Spells.NIF.optimize.SpellCleanRefLists,
        PyFFI.Spells.NIF.optimize.SpellMergeDuplicates,
        PyFFI.Spells.NIF.optimize.SpellOptimizeGeometry,
        PyFFI.Spells.NIF.optimize.SpellOptimize,
        optimize_split,
        scale,
        updatecenterradius,
        updatemopp,
        updateskinpartition]
    ALIASDICT = {
        "texdump": "dump_tex",
        "read": "check_read",
        "readwrite": "check_readwrite",
        "ffvt3rskinpartition": "fix_ffvt3rskinpartition",
        "disableparallax": "fix_disableparallax",
        "exportpixeldata": "dump_pixeldata"}
    EXAMPLES = """* check if PyFFI can read all files in current directory
  (python version of nifskope's xml checker):

    python niftoaster.py check_read .

* optimize all nif files a directory tree, recursively

    python niftoaster.py optimize /path/to/your/nifs/

* print texture information of all nif files a directory tree, recursively

    python niftoaster.py dump_tex /path/to/your/nifs/

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
    NifToaster().cli()

