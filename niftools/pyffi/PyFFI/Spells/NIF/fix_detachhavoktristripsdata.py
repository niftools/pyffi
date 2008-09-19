"""For NiTriStrips if their NiTriStripsData also occurs in a
bhkNiTriStripsShape, make deep copy of data in havok. This is mainly
useful as a preperation for other spells that act on NiTriStripsData,
to ensure that the havok data remains untouched."""
# this spell solves issue #2065018, MiddleWolfRug01.NIF

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

from PyFFI.Formats.NIF import NifFormat

# set flag to overwrite files
__readonly__ = False

def testRoot(root, **args):
    """This is the main entry point for the script.

    @param root: The root of the tree.
    @type root: L{NifFormat.NiObject}
    """
    # check which blocks to exclude
    exclude = args.get("exclude", [])
    if "NiTriStripsData" in exclude:
        return

    # get list of all blocks
    block_list = [ block for block in root.tree() ]

    # check for shared NiTriStripsData, and detach if necessary
    for block in block_list:
        if isinstance(block, NifFormat.bhkNiTriStripsShape):
            for i, shape in enumerate(block.stripsData):
                for otherblock in block_list:
                    if isinstance(otherblock, NifFormat.NiTriStrips):
                        if shape is otherblock.data:
                            print("detaching data of %s from havok tree"
                                  % otherblock.name)
                            block.stripsData[i] = NifFormat.NiTriStripsData().deepcopy(shape)
