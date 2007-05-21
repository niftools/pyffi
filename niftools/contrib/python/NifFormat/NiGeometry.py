# --------------------------------------------------------------------------
# NifFormat.NiGeometry
# Custom functions for NiGeometry.
# --------------------------------------------------------------------------
# ***** BEGIN LICENCE BLOCK *****
#
# Copyright (c) 2007, NIF File Format Library and Tools.
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

def isSkin(self):
    return self.skinInstance != None

def _validateSkin(self):
    """Check that skinning blocks are valid. Will raise ValueError exception
    if not."""
    if self.skinInstance == None: return
    if self.skinInstance.data == None:
        raise ValueError('NiGeometry has NiSkinInstance without NiSkinData')
    if self.skinInstance.skeletonRoot == None:
        raise ValueError('NiGeometry has NiSkinInstance without skeleton root')
    if self.skinInstance.numBones != self.skinInstance.data.numBones:
        raise ValueError('NiSkinInstance and NiSkinData have different number of bones')

def getBoneRestPositions(self):
    """Return bone rest position dictionary, in skeleton root space.
    To find the rest positions in global space, post-multiply with
    skinInstance.skeletonRoot.getTransform()."""
    if not self.isSkin(): return {} # no bones
    self._validateSkin() # check that skin data is valid
    # calculate the rest positions
    # (there could be an inverse less, code is written to be clear rather
    # than to be fast)
    restpose_dct = {}
    skininst = self.skinInstance
    skindata = skininst.data
    geometry_matrix = skindata.getTransform().getInverse()
    for i, bone_block in enumerate(skininst.bones):
        bone_matrix = skindata.boneList[i].getTransform().getInverse()
        restpose_dct[bone_block] = bone_matrix * geometry_matrix
    return restpose_dct

def setBoneRestPositions(self, restpose_dct):
    """Recalculate the data which fixes the bone rest positions, from
    the bone rest position (in skeleton root space) dictionary."""
    self._validateSkin() # check that skin data is valid
    skininst = self.skinInstance
    skindata = skininst.data
    skelroot = skininst.skeletonRoot
    # calculate skin data from rest positions
    # (there could be an inverse less, code is written to be clear rather
    # than to be fast)
    geometry_matrix = self.getTransform(skelroot)
    skindata.setTransform(geometry_matrix.getInverse())
    for i, bone_block in enumerate(skininst.bones):
        bone_matrix = restpose_dct[bone_block] * geometry_matrix.getInverse()
        skindata.boneList[i].setTransform(bone_matrix.getInverse())
    return restpose_dct
