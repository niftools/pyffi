"""Module which contains all spells that fix something in a nif."""

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

class SpellDelTangentSpace(NifSpell):
    """Delete tangentspace if it is present."""

    SPELLNAME = "fix_deltangentspace"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiBinaryExtraData)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have tangent space data?
            for extra in branch.getExtraDatas():
                if isinstance(extra, NifFormat.NiBinaryExtraData):
                    if (extra.name ==
                        'Tangent space (binormal & tangent vectors)'):
                        self.toaster.msg("removing tangent space block")
                        branch.removeExtraData(extra)
            # all extra blocks here done; no need to recurse further
            return False
        # recurse further
        return True

class SpellAddTangentSpace(NifSpell):
    """Add tangentspace if none is present."""

    SPELLNAME = "fix_addtangentspace"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiBinaryExtraData)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have tangent space data?
            for extra in branch.getExtraDatas():
                if isinstance(extra, NifFormat.NiBinaryExtraData):
                    if (extra.name ==
                        'Tangent space (binormal & tangent vectors)'):
                        # tangent space found, done!
                        return False
            # no tangent space found
            self.toaster.msg("adding tangent space")
            branch.updateTangentSpace()
            # all extra blocks here done; no need to recurse further
            return False
        else:
            # recurse further
            return True

class SpellFFVT3RSkinPartition(NifSpell):
    """Create or update skin partition, with settings that work for Freedom
    Force vs. The 3rd Reich."""

    SPELLNAME = "fix_ffvt3rskinpartition"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiSkinInstance)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # if the branch has skinning info
            if branch.skinInstance:
                # then update the skin partition
                self.toaster.msg("updating skin partition")
                branch.updateSkinPartition(
                    maxbonesperpartition=4, maxbonespervertex=4,
                    stripify=False, verbose=0, padbones=True)
            return False
            # done; no need to recurse further in this branch
        else:
            # recurse further
            return True

class SpellFixTexturePath(NifSpell):
    """Fix the texture path. Transforms 0x0a into \\n and 0x0d into \\r.
    This fixes a bug in nifs saved with older versions of nifskope.
    Also transforms / into \\. This fixes problems when packing files into
    a bsa archive."""

    SPELLNAME = "fix_texturepath"
    READONLY = False

    def datainspect(self):
        # only run the spell if there are NiSourceTexture blocks
        return self.inspectblocktype(NifFormat.NiSourceTexture)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch, texturing properties and source
        # textures
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTexturingProperty,
                                   NifFormat.NiSourceTexture))
    
    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiSourceTexture):
            if (('\n' in branch.fileName)
                or ('\r' in branch.fileName)
                or ('/' in branch.fileName)):
                branch.fileName = branch.fileName.replace('\n', '\\n')
                branch.fileName = branch.fileName.replace('\r', '\\r')
                branch.fileName = branch.fileName.replace('/', '\\')
                self.toaster.msg("fixed file name '%s'" % branch.fileName)
            return False
        else:
            return True

# the next spell solves issue #2065018, MiddleWolfRug01.NIF
class SpellDetachHavokTriStripsData(NifSpell):
    """For NiTriStrips if their NiTriStripsData also occurs in a
    bhkNiTriStripsShape, make deep copy of data in havok. This is
    mainly useful as a preperation for other spells that act on
    NiTriStripsData, to ensure that the havok data remains untouched."""

    SPELLNAME = "fix_detachhavoktristripsdata"
    READONLY = False

    def __init__(self, *args, **kwargs):
        NifSpell.__init__(self, *args, **kwargs)
        # provides the bhknitristripsshapes within the current NiTriStrips
        self.bhknitristripsshapes = None

    def datainspect(self):
        # only run the spell if there are bhkNiTriStripsShape blocks
        return self.inspectblocktype(NifFormat.bhkNiTriStripsShape)

    def dataentry(self):
        # build list of all NiTriStrips blocks
        self.nitristrips = [branch for branch in self.data.getGlobalTree()
                            if isinstance(branch, NifFormat.NiTriStrips)]
        if self.nitristrips:
            return True
        else:
            return False

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch and collision branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.bhkCollisionObject,
                                   NifFormat.bhkRefObject))
    
    def branchentry(self, branch):
        if isinstance(branch, NifFormat.bhkNiTriStripsShape):
            for i, data in enumerate(branch.stripsData):
                if data in [otherbranch.data
                            for otherbranch in self.nitristrips]:
                        # detach!
                        self.toaster.msg("detaching havok data")
                        branch.stripsData[i] = NifFormat.NiTriStripsData().deepcopy(data)
            return False
        else:
            return True

class SpellClampMaterialAlpha(NifSpell):
    """Clamp corrupted material alpha values."""

    SPELLNAME = "fix_clampmaterialalpha"
    READONLY = False

    def datainspect(self):
        # only run the spell if there are material property blocks
        return self.inspectblocktype(NifFormat.NiMaterialProperty)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch, and material properties
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiMaterialProperty))
    
    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiMaterialProperty):
            # check if alpha exceeds usual values
            if branch.alpha > 1:
                # too large
                self.toaster.msg(
                    "clamping alpha value (%f -> 1.0)" % branch.alpha)
                branch.alpha = 1.0
            elif branch.alpha < 0:
                # too small
                self.toaster.msg(
                    "clamping alpha value (%f -> 0.0)" % branch.alpha)
                branch.alpha = 0.0
            # stop recursion
            return False
        else:
            # keep recursing into children
            return True
