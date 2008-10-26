"""Spells for dumping particular blocks from nifs."""

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
from PyFFI.Spells.NIF import NifSpell

def dumpArray(arr):
    """Format an array.

    @param arr: An array.
    @type arr: L{PyFFI.ObjectModels.XML.Array.Array}
    @return: String describing the array.
    """
    text = ""
    if arr._count2 == None:
        for i, element in enumerate(list.__iter__(arr)):
            if i > 16:
                text += "etc...\n"
                break
            text += "%i: %s\n" % (i, dumpAttr(element))
    else:
        k = 0
        for i, elemlist in enumerate(list.__iter__(arr)):
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
    """Return formatted string for block without following references.

    @param block: The block to print.
    @type block: L{NifFormat.NiObject}
    @return: String string describing the block.
    """
    text = '%s instance at 0x%08X\n' % (block.__class__.__name__, id(block))
    for attr in block._filteredAttributeList():
        attr_str_lines = \
            dumpAttr(getattr(block, "_%s_value_" % attr.name)).splitlines()
        if len(attr_str_lines) > 1:
            text += '* %s :\n' % attr.name
            for attr_str in attr_str_lines:
                text += '    %s\n' % attr_str
        else:
            text += '* %s : %s\n' % (attr.name, attr_str_lines[0])
    return text

def dumpAttr(attr):
    """Format an attribute.

    @param attr: The attribute to print.
    @type attr: (anything goes)
    @return: String for the attribute.
    """
    if isinstance(attr, (NifFormat.Ref, NifFormat.Ptr)):
        ref = attr.getValue()
        if ref:
            return "<%s instance at 0x%08X>" % (ref.__class__.__name__,
                                                id(attr))
        else:
            return "<None>"
    elif isinstance(attr, list):
        return dumpArray(attr)
    elif isinstance(attr, NifFormat.NiObject):
        return dumpBlock(attr)
    else:
        return str(attr)

class SpellDumpAll(NifSpell):
    """Dump the whole nif file."""

    SPELLNAME = "dump"

    def branchentry(self, branch):
        # dump it
        self.toaster.msg(dumpBlock(branch))
        # continue recursion
        return True
