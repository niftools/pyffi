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

"""
The nif skinning algorithm works as follows (as of nifskope):
v'                               # vertex after skinning in geometry space
= sum_{b\in skininst.bones}      # sum over all bones b that influence the mesh
weight[v][b]                     # how much bone b influences vertex v
* v                              # vertex before skinning in geometry space (as it is stored in the shape data)
* skindata.bonelist[b].transform # transform vertex to bone b space in the rest pose
* b.transform(skelroot)          # apply animation, by multiplying with all bone matrices in the chain down to the skeleton root; the vertex is now in skeleton root space
* skindata.transform             # transforms vertex from skeleton root space back to geometry space
"""

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

def getGeometryRestPosition(self):
    """Return geometry rest position, in skeleton root space."""
    if not self.isSkin():
        raise ValueError('NiGeometry has no NiSkinInstance, and therefore no rest position')
    self._validateSkin() # check that skin data is valid
    # calculate the rest positions
    # (there could be an inverse less, code is written to be clear rather
    # than to be fast)
    skininst = self.skinInstance
    skindata = skininst.data
    return skindata.getTransform() * self.getTransform(skininst.skeletonRoot)

def getBoneRestPositions(self):
    """Return bone rest position dictionary, in skeleton root space."""
    # first get the geometry rest position
    geometry_matrix = self.getGeometryRestPosition()
    # calculate the rest positions
    restpose_dct = {}
    skininst = self.skinInstance
    skindata = skininst.data
    for i, bone_block in enumerate(skininst.bones):
        restpose_dct[bone_block] = skindata.boneList[i].getTransform().getInverse()
    return restpose_dct

def flattenSkin(self):
    """Reposition all bone blocks and geometry block in the tree to be direct
    children of the skeleton root."""

    if not self.isSkin(): return # nothing to do
    self._validateSkin() # validate the skin
    skininst = self.skinInstance
    skindata = skininst.data
    skelroot = skininst.skeletonRoot

    # reparent geometry
    self.setTransform(skindata.getTransform() * self.getTransform(skelroot))
    chain = skelroot.findChain(self)
    skelroot.removeChild(chain[1]) # detatch geometry from tree
    skelroot.addChild(self, front = True) # and attatch it to the skeleton root

    # reparent bones and set their transforms
    for i, bone_block in enumerate(skininst.bones):
        if bone_block != skelroot:
            # remove children
            bone_block.numChildren = 0
            bone_block.children.updateSize()
            bone_block.setTransform(skindata.boneList[i].getTransform().getInverse())
            skelroot.addChild(bone_block)

