"""Custom functions for NiGeometry.

>>> from PyFFI.NIF import NifFormat
>>> id44 = NifFormat.Matrix44()
>>> id44.setIdentity()
>>> skelroot = NifFormat.NiNode()
>>> skelroot.name = 'skelroot'
>>> skelroot.setTransform(id44)
>>> bone1 = NifFormat.NiNode()
>>> bone1.name = 'bone1'
>>> bone1.setTransform(id44)
>>> bone2 = NifFormat.NiNode()
>>> bone2.name = 'bone2'
>>> bone2.setTransform(id44)
>>> bone21 = NifFormat.NiNode()
>>> bone21.name = 'bone21'
>>> bone21.setTransform(id44)
>>> bone22 = NifFormat.NiNode()
>>> bone22.name = 'bone22'
>>> bone22.setTransform(id44)
>>> bone211 = NifFormat.NiNode()
>>> bone211.name = 'bone211'
>>> bone211.setTransform(id44)
>>> skelroot.addChild(bone1)
>>> bone1.addChild(bone2)
>>> bone2.addChild(bone21)
>>> bone2.addChild(bone22)
>>> bone21.addChild(bone211)
>>> geom = NifFormat.NiTriShape()
>>> geom.name = 'geom'
>>> geom.setTransform(id44)
>>> geomdata = NifFormat.NiTriShapeData()
>>> skininst = NifFormat.NiSkinInstance()
>>> skindata = NifFormat.NiSkinData()
>>> skelroot.addChild(geom)
>>> geom.data = geomdata
>>> geom.skinInstance = skininst
>>> skininst.skeletonRoot = skelroot
>>> skininst.data = skindata
>>> skininst.numBones = 4
>>> skininst.bones.updateSize()
>>> skininst.bones[0] = bone1
>>> skininst.bones[1] = bone2
>>> skininst.bones[2] = bone22
>>> skininst.bones[3] = bone211
>>> skindata.numBones = 4
>>> skindata.boneList.updateSize()
>>> print [ child.name for child in skelroot.children ]
['bone1', 'geom']
>>> skindata.setTransform(id44)
>>> for bonedata in skindata.boneList:
...     bonedata.setTransform(id44)
>>> affectedbones = geom.flattenSkin()
>>> print [ bone.name for bone in affectedbones ]
['bone1', 'bone2', 'bone22', 'bone211']
>>> print [ child.name for child in skelroot.children ]
['geom', 'bone1', 'bone21', 'bone2', 'bone22', 'bone211']
"""

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

def isSkin(self):
    """Returns True if geometry is skinned."""
    return self.skinInstance != None

def _validateSkin(self):
    """Check that skinning blocks are valid. Will raise NifError exception
    if not."""
    if self.skinInstance == None: return
    if self.skinInstance.data == None:
        raise self.cls.NifError('NiGeometry has NiSkinInstance without NiSkinData')
    if self.skinInstance.skeletonRoot == None:
        raise self.cls.NifError('NiGeometry has NiSkinInstance without skeleton root')
    if self.skinInstance.numBones != self.skinInstance.data.numBones:
        raise self.cls.NifError('NiSkinInstance and NiSkinData have different number of bones')

def addBone(self, bone, vert_weights):
    """Add bone with given vertex weights.
    After adding all bones, the geometry skinning information should be set
    from the current position of the bones using the L{updateBindPosition} function.

    @param bone: The bone NiNode block.
    @param vert_weights: A dictionary mapping each influenced vertex index to a vertex weight."""
    self._validateSkin()
    skininst = self.skinInstance
    skindata = skininst.data
    skelroot = skininst.skeletonRoot

    bone_index = skininst.numBones
    skininst.numBones = bone_index+1
    skininst.bones.updateSize()
    skininst.bones[bone_index] = bone
    skindata.numBones = bone_index+1
    skindata.boneList.updateSize()
    skinbonedata = skindata.boneList[bone_index]
    # set vertex weights
    skinbonedata.numVertices = len(vert_weights)
    skinbonedata.vertexWeights.updateSize()
    for i, (vert_index, vert_weight) in enumerate(vert_weights.iteritems()):
        skinbonedata.vertexWeights[i].index = vert_index
        skinbonedata.vertexWeights[i].weight = vert_weight



def getVertexWeights(self):
    """Get vertex weights in a convenient format: list bone and weight per
    vertex."""
    # shortcuts relevant blocks
    if not self.skinInstance:
        raise self.cls.NifError('Cannot get vertex weights of geometry without skin.')
    self._validateSkin()
    geomdata = self.data
    skininst = self.skinInstance
    skindata = skininst.data
    weights = [[] for i in xrange(geomdata.numVertices)]
    for bonenum, bonedata in enumerate(skindata.boneList):
        for skinweight in bonedata.vertexWeights:
            weights[skinweight.index].append([bonenum, skinweight.weight])
    return weights


def flattenSkin(self):
    """Reposition all bone blocks and geometry block in the tree to be direct
    children of the skeleton root.

    Returns list of all used bones by the skin."""

    if not self.isSkin(): return [] # nothing to do

    result = [] # list of repositioned bones
    self._validateSkin() # validate the skin
    skininst = self.skinInstance
    skindata = skininst.data
    skelroot = skininst.skeletonRoot

    # reparent geometry
    self.setTransform(self.getTransform(skelroot))
    geometry_parent = skelroot.findChain(self, block_type = self.cls.NiAVObject)[-2]
    geometry_parent.removeChild(self) # detatch geometry from tree
    skelroot.addChild(self, front = True) # and attatch it to the skeleton root

    # reparent all the bone blocks
    for bone_block in skininst.bones:
        # skeleton root, if it is used as bone, does not need to be processed
        if bone_block == skelroot: continue
        # get bone parent
        bone_parent = skelroot.findChain(bone_block, block_type = self.cls.NiAVObject)[-2]
        # set new child transforms
        for child in bone_block.children:
            child.setTransform(child.getTransform(bone_parent))
        # reparent children
        for child in bone_block.children:
            bone_parent.addChild(child)
        bone_block.numChildren = 0
        bone_block.children.updateSize() # = removeChild on each child
        # set new bone transform
        bone_block.setTransform(bone_block.getTransform(skelroot))
        # reparent bone block
        bone_parent.removeChild(bone_block)
        skelroot.addChild(bone_block)
        result.append(bone_block)

    return result



def mergeSkeletonRoots(self):
    """This function will look for other geometries
    1) whose skeleton root is a (possibly indirect) child of the skeleton root
    of this skin, and
    2) whose skeleton shares bones with this geometry's skin.
    It will then reparent those geometries to the skeleton
    root of this geometry. For example, it will unify the skeleton
    roots in Morrowind's cliffracer.nif file. This makes it much easier to
    import skeletons in for instance Blender: there will be only one skeleton
    root for each bone, over all geometries.

    The merge fails if some transforms are not unit transform.
    
    Returns list of all new blocks that have been reparented (and added
    to the skeleton root children list), and a list of blocks for which the
    merge failed."""

    if not self.isSkin(): return [], [] # nothing to do

    result = [] # list of reparented blocks
    failed = [] # list of blocks that could not be reparented
    self._validateSkin() # validate the skin
    skininst = self.skinInstance
    skelroot = skininst.skeletonRoot

    id44 = self.cls.Matrix44()
    id44.setIdentity()

    # look for geometries are in this skeleton root's tree
    # that have a different skeleton root
    # and that share bones with this geometry
    geoms = [block for block in skelroot.tree() if isinstance(block, self.cls.NiGeometry) and block.isSkin() and block.skinInstance.skeletonRoot != skelroot and set(block.skinInstance.bones) & set(skininst.bones)]
    
    # find the root block (direct parent of skeleton root that connects to the geometry) for each of these geometries
    geomroots = {}
    for geom in geoms:
        # check transforms
        if geom.skinInstance.data.getTransform() != id44 or geom.getTransform(geom.skinInstance.skeletonRoot)!= id44:
            failed.append(geom)
            continue # skip this one
        # find geometry root block
        chain = geom.skinInstance.skeletonRoot.findChain(geom)
        geomroots[geom] = chain[1]

    # reparent geometries
    for geom, geomroot in geomroots.iteritems():
        # reparent
        geom.skinInstance.skeletonRoot.removeChild(geomroot) # detatch geometry from chain
        skelroot.addChild(geomroot) # attach to new skeleton root
        geom.skinInstance.skeletonRoot = skelroot # set its new skeleton root
        if geomroot not in result:
            result.append(geomroot) # and signal that we reparented this block

    return result, failed



# The nif skinning algorithm works as follows (as of nifskope):
# v'                               # vertex after skinning in geometry space
# = sum over {b in skininst.bones} # sum over all bones b that influence the mesh
# weight[v][b]                     # how much bone b influences vertex v
# * v                              # vertex before skinning in geometry space (as it is stored in the shape data)
# * skindata.boneList[b].transform # transform vertex to bone b space in the rest pose
# * b.getTransform(skelroot)       # apply animation, by multiplying with all bone matrices in the chain down to the skeleton root; the vertex is now in skeleton root space
# * skindata.transform             # transforms vertex from skeleton root space back to geometry space
def getSkinDeformation(self):
    """Returns a list of vertices and normals in their final position after
    skinning, in geometry space."""

    if not self.data: return [], []

    if not self.isSkin(): return self.data.vertices, self.data.normals

    self._validateSkin()
    skininst = self.skinInstance
    skindata = skininst.data
    skelroot = skininst.skeletonRoot

    vertices = [ self.cls.Vector3() for i in xrange(self.data.numVertices) ]
    normals = [ self.cls.Vector3() for i in xrange(self.data.numVertices) ]
    sumweights = [ 0.0 for i in xrange(self.data.numVertices) ]
    skin_offset = skindata.getTransform()
    for i, bone_block in enumerate(skininst.bones):
        bonedata = skindata.boneList[i]
        bone_offset = bonedata.getTransform()
        bone_matrix = bone_block.getTransform(skelroot)
        transform = bone_offset * bone_matrix * skin_offset
        scale, rotation, translation = transform.getScaleRotationTranslation()
        for skinweight in bonedata.vertexWeights:
            index = skinweight.index
            weight = skinweight.weight
            vertices[index] += weight * (self.data.vertices[index] * transform)
            if self.data.hasNormals:
                normals[index] += weight * (self.data.normals[index] * rotation)
            sumweights[index] += weight

    for i, s in enumerate(sumweights):
        if abs(s - 1.0) > 0.01: print "WARNING: vertex %i has weights not summing to one in getSkinDeformation"

    return vertices, normals



# ported and extended from niflib::NiNode::GoToSkeletonBindPosition() (r2518)
def sendBonesToBindPosition(self):
    """Send all bones to their bind position."""
    if not self.isSkin(): return

    # validate skin and set up quick links
    self._validateSkin()
    skininst = self.skinInstance
    skindata = skininst.data
    skelroot = skininst.skeletonRoot

    # reposition the bones
    for i, parent_bone in enumerate(skininst.bones):
        parent_offset = skindata.boneList[i].getTransform()
        # if parent_bone is a child of the skeleton root, then fix its
        # transfrom
        if parent_bone in skelroot.children:
            parent_bone.setTransform(parent_offset.getInverse() * self.getTransform(skelroot))
        # fix the transform of all its the children
        for j, child_bone in enumerate(skininst.bones):
            if child_bone not in parent_bone.children: continue
            child_offset = skindata.boneList[j].getTransform()
            child_matrix = child_offset.getInverse() * parent_offset
            child_bone.setTransform(child_matrix)



# ported from niflib::NiSkinData::ResetOffsets (r2561)
def updateBindPosition(self):
    """Make current position of the bones the bind position for this geometry.

    Sets the NiSkinData overall transform to the inverse of the geometry transform
    relative to the skeleton root, and sets the NiSkinData of each bone to
    the geometry transform relative to the skeleton root times the inverse of the bone
    transform relative to the skeleton root."""
    if not self.isSkin(): return

    # validate skin and set up quick links
    self._validateSkin()
    skininst = self.skinInstance
    skindata = skininst.data
    skelroot = skininst.skeletonRoot

    # calculate overall offset
    geomtransform = self.getTransform(skelroot)
    skindata.setTransform(geomtransform.getInverse())

    # calculate bone offsets
    for i, bone in enumerate(skininst.bones):
         skindata.boneList[i].setTransform(geomtransform * bone.getTransform(skelroot).getInverse())

