"""Module which contains all spells that check something in a nif file."""

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

import tempfile

from PyFFI.Formats.NIF import NifFormat
from PyFFI.Spells.NIF import NifSpell

class SpellReadWrite(NifSpell):
    """Like the original read-write spell, but with additional file size
    check."""

    SPELLNAME = "check_readwrite"

    def dataentry(self):
        self.toaster.msgblockbegin("writing to temporary file")

        f_tmp = tempfile.TemporaryFile()
        try:
            self.data.write(f_tmp)
            # comparing the files will usually be different because
            # blocks may have been written back in a different order,
            # so cheaply just compare file sizes
            self.toaster.msg("comparing file sizes")
            self.stream.seek(0, 2)
            f_tmp.seek(0, 2)
            if self.stream.tell() != f_tmp.tell():
                self.toaster.msg("original size: %i" % self.stream.tell())
                self.toaster.msg("written size:  %i" % f_tmp.tell())
                f_tmp.seek(0)
                f_debug = open("debug.nif", "wb")
                f_debug.write(f_tmp.read(-1))
                f_debug.close()
                raise StandardError('write check failed: file sizes differ (written file saved as debug.nif for inspection)')
        finally:
            f_tmp.close()
    
        self.toaster.msgblockend()

        # spell is finished: prevent recursing into the tree
        return False

class SpellNodeNamesByFlag(NifSpell):
    """This spell goes over all nif files, and at the end, it gives a summary
    of which node names where used with particular flags."""

    SPELLNAME = "check_nodenamesbyflag"

    @classmethod
    def toastentry(cls, toaster):
        toaster.flagdict = {}
        return True

    @classmethod
    def toastexit(cls, toaster):
        for flag, names in toaster.flagdict.iteritems():
            print flag, names

    def datainspect(self):
        return self.data.header.hasBlockType(NifFormat.NiNode)

    def branchinspect(self, branch):
        # stick to main tree
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiAVObject):
            if not branch.flags in self.toaster.flagdict:
                self.toaster.flagdict[branch.flags] = []
            if not branch.name in self.toaster.flagdict[branch.flags]:
                self.toaster.flagdict[branch.flags].append(branch.name)
            return True
        else:
            return False

