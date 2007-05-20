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

def getBoneRestPositions(self):
    """Return bone rest position dictionary, in skeleton root space.
    To find the rest positions in global space, post-multiply with
    skinInstance.skeletonRoot.getTransform()."""
    restpose_dct = {}
    # check out the geometry skin
    skininst = self.skinInstance
    if self.skinInstance == None: return {} # no bones
    skindata = skininst.data
    if skindata == None:
        raise ValueError('NiGeometry has NiSkinInstance without NiSkinData')
    skelroot = skininst.skeletonRoot
    if skelroot == None:
        raise ValueError('NiGeometry has NiSkinInstance without skeleton root')
    num_bones = skininst.numBones
    if num_bones != skindata.numBones:
        raise ValueError('NiSkinInstance and NiSkinData have different number of bones')
    # calculate the rest positions
    geometry_matrix = skindata.getTransform()
    for i, bone_block in enumerate(skininst.bones):
        bone_matrix = skindata.boneList[i].getTransform()
        restpose_dct[bone_block] = (geometry_matrix * bone_matrix).getInverse()
    return restpose_dct

def setBoneRestPositions(self, restpose_dct):
    """Recalculate the data which fixes the bone rest positions, from
    the bone rest position (in skeleton root space) dictionary."""
    raise NotImplementedError
