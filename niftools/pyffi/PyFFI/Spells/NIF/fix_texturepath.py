"""Fix texture path."""

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

# flag overwrite
__readonly__ = False

def testBlock(block, **args):
    """Fix the texture path. Transforms 0x0a into \\n and 0x0d into \\r.
    This fixes a bug in nifs saved with older versions of nifskope.
    Also transforms / into \\. This fixes problems when packing files into
    a bsa archive.

    @param block: The block to fix.
    @type block: L{NifFormat.NiSourceTexture}
    """
    # does it apply on this block?
    if not isinstance(block, NifFormat.NiSourceTexture):
        return

    # is this block excluded?
    exclude = args.get("exclude", [])
    if "NiSourceTexture" in exclude:
        return

    if (('\n' in block.fileName)
        or ('\r' in block.fileName)
        or ('\\' in block.fileName)):
        block.fileName = block.fileName.replace('\n', '\\n')
        block.fileName = block.fileName.replace('\r', '\\r')
        block.fileName = block.fileName.replace('/', '\\')
        print("fixing corrupted file name")
        print("  %s" % block.fileName)
