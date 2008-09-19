"""A spell for splitting geometries in order to limit the maximal radius,
which results in nif files that run much smoother in the engine."""

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

from itertools import izip

from PyFFI.Formats.NIF import NifFormat
from PyFFI.Utils import TriStrip
from PyFFI.Spells.NIF import fix_detachhavoktristripsdata

# set flag to overwrite files
__readonly__ = False

# example usage
__examples__ = """* Standard usage:

    python niftoaster.py optimize_split /path/to/copy/of/my/nifs
"""

def testRoot(root, **args):
    """Optimize the tree at root. This is the main entry point for the
    optimize script.

    @param root: The root of the tree.
    @type root: L{NifFormat.NiObject}
    """
    # detach havok tristripsdata
    fix_detachhavoktristripsdata.testRoot(root, **args)

    # check which blocks to exclude
    exclude = args.get("exclude", [])

    # get list of all blocks
    block_list = [ block for block in root.tree(unique = True) ]

    # TODO: finish
