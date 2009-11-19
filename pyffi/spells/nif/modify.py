"""Module which contains all spells that modify a nif (anything that
is not a fix).
"""

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

from pyffi.formats.nif import NifFormat
from pyffi.spells.nif import NifSpell
import pyffi.spells.nif
import pyffi.spells.nif.check # recycle checking spells for update spells
import os

class SpellTexturePath(NifSpell):
    """Changes the texture path while keeping the texture names."""

    SPELLNAME = "modify_texturepath"
    READONLY = False

    @classmethod
    def toastentry(cls, toaster):
        if not toaster.options["arg"]:
            toaster.logger.warn(
                "must specify path as argument "
                "(e.g. -a textures\\pm\\dungeons\\bloodyayleid\\interior) "
                "to apply spell")
            return False
        else:
            toaster.texture_path = str(toaster.options["arg"])
            # standardize the path
            toaster.texture_path = toaster.texture_path.replace("/", os.sep)
            toaster.texture_path = toaster.texture_path.replace("\\", os.sep)
            return True

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiSourceTexture)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTexturingProperty,
                                   NifFormat.NiSourceTexture))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiSourceTexture):
            old_file_name = str(branch.fileName) # for reporting
            # note: replace backslashes by os.sep in filename, and
            # when joined, revert them back, for linux
            branch.fileName = os.path.join(
                self.toaster.texture_path,
                os.path.basename(old_file_name.replace("\\", os.sep))
                ).replace(os.sep, "\\") 
            self.toaster.msg("%s -> %s" % (old_file_name, branch.fileName))
            # all textures done no need to recurse further.
            return False
        else:
            # recurse further
            return True
