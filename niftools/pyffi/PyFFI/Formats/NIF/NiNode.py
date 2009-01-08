"""Custom functions for NiNode.

Doctests
========

Old test code
-------------

>>> from PyFFI.Formats.NIF import NifFormat
>>> x = NifFormat.NiNode()
>>> y = NifFormat.NiNode()
>>> z = NifFormat.NiNode()
>>> x.numChildren =1
>>> x.children.updateSize()
>>> y in x.children
False
>>> x.children[0] = y
>>> y in x.children
True
>>> x.addChild(z, front = True)
>>> x.addChild(y)
>>> x.numChildren
2
>>> x.children[0] is z
True
>>> x.removeChild(y)
>>> y in x.children
False
>>> x.numChildren
1
>>> e = NifFormat.NiSpotLight()
>>> x.addEffect(e)
>>> x.numEffects
1
>>> e in x.effects
True

Children
--------

>>> from PyFFI.Formats.NIF import NifFormat
>>> node = NifFormat.NiNode()
>>> child1 = NifFormat.NiNode()
>>> child1.name = "hello"
>>> child2 = NifFormat.NiNode()
>>> child2.name = "world"
>>> node.getChildren()
[]
>>> node.setChildren([child1, child2])
>>> [child.name for child in node.getChildren()]
['hello', 'world']
>>> [child.name for child in node.children]
['hello', 'world']
>>> node.setChildren([])
>>> node.getChildren()
[]
>>> # now set them the other way around
>>> node.setChildren([child2, child1])
>>> [child.name for child in node.getChildren()]
['world', 'hello']
>>> [child.name for child in node.children]
['world', 'hello']
>>> node.removeChild(child2)
>>> [child.name for child in node.children]
['hello']
>>> node.addChild(child2)
>>> [child.name for child in node.children]
['hello', 'world']

Effects
-------

>>> from PyFFI.Formats.NIF import NifFormat
>>> node = NifFormat.NiNode()
>>> effect1 = NifFormat.NiSpotLight()
>>> effect1.name = "hello"
>>> effect2 = NifFormat.NiSpotLight()
>>> effect2.name = "world"
>>> node.getEffects()
[]
>>> node.setEffects([effect1, effect2])
>>> [effect.name for effect in node.getEffects()]
['hello', 'world']
>>> [effect.name for effect in node.effects]
['hello', 'world']
>>> node.setEffects([])
>>> node.getEffects()
[]
>>> # now set them the other way around
>>> node.setEffects([effect2, effect1])
>>> [effect.name for effect in node.getEffects()]
['world', 'hello']
>>> [effect.name for effect in node.effects]
['world', 'hello']
>>> node.removeEffect(effect2)
>>> [effect.name for effect in node.effects]
['hello']
>>> node.addEffect(effect2)
>>> [effect.name for effect in node.effects]
['hello', 'world']
"""

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

from itertools import izip
import logging

def addChild(self, child, front=False):
    """Add block to child list.

    @param child: The child to add.
    @type child: L{NifFormat.NiAVObject}
    @kwarg front: Whether to add to the front or to the end of the
        list (default is at end).
    @type front: C{bool}
    """
    # check if it's already a child
    if child in self.children:
        return
    # increase number of children
    num_children = self.numChildren
    self.numChildren = num_children + 1
    self.children.updateSize()
    # add the child
    if not front:
        self.children[num_children] = child
    else:
        for i in xrange(num_children, 0, -1):
            self.children[i] = self.children[i-1]
        self.children[0] = child

def removeChild(self, child):
    """Remove a block from the child list.

    @param child: The child to remove.
    @type child: L{NifFormat.NiAVObject}
    """
    self.setChildren([otherchild for otherchild in self.getChildren()
                      if not(otherchild is child)])

def getChildren(self):
    """Return a list of the children of the block.

    @return: The list of children.
    @rtype: C{list} of L{NifFormat.NiAVObject}
    """
    return [child for child in self.children]

def setChildren(self, childlist):
    """Set the list of children from the given list (destroys existing list).

    @param childlist: The list of child blocks to set.
    @type childlist: C{list} of L{NifFormat.NiAVObject}
    """
    self.numChildren = len(childlist)
    self.children.updateSize()
    for i, child in enumerate(childlist):
        self.children[i] = child

def addEffect(self, effect):
    """Add an effect to the list of effects.

    @param effect: The effect to add.
    @type effect: L{NifFormat.NiDynamicEffect}
    """
    num_effs = self.numEffects
    self.numEffects = num_effs + 1
    self.effects.updateSize()
    self.effects[num_effs] = effect

def removeEffect(self, effect):
    """Remove a block from the effect list.

    @param effect: The effect to remove.
    @type effect: L{NifFormat.NiDynamicEffect}
    """
    self.setEffects([othereffect for othereffect in self.getEffects()
                     if not(othereffect is effect)])

def getEffects(self):
    """Return a list of the effects of the block.

    @return: The list of effects.
    @rtype: C{list} of L{NifFormat.NiDynamicEffect}
    """
    return [effect for effect in self.effects]

def setEffects(self, effectlist):
    """Set the list of effects from the given list (destroys existing list).

    @param effectlist: The list of effect blocks to set.
    @type effectlist: C{list} of L{NifFormat.NiDynamicEffect}
    """
    self.numEffects = len(effectlist)
    self.effects.updateSize()
    for i, effect in enumerate(effectlist):
        self.effects[i] = effect

def mergeExternalSkeletonRoot(self, skelroot):
    """Attach skinned geometry to self (which will be the new skeleton root of
    the nif at the given skeleton root). Use this function if you move a
    skinned geometry from one nif into a new nif file. The bone links will be
    updated to point to the tree at self, instead of to the external tree.
    """
    # sanity check
    if self.name != skelroot.name:
        raise ValueError("skeleton root names do not match")

    # get a dictionary mapping bone names to bone blocks
    bone_dict = {}
    for block in self.tree():
        if isinstance(block, self.cls.NiNode):
            if block.name:
                if block.name in bone_dict:
                    raise ValueError(
                        "multiple NiNodes with name %s" % block.name)
                bone_dict[block.name] = block

    # add all non-bone children of the skeleton root to self
    for child in skelroot.getChildren():
        # skip empty children
        if not child:
            continue
        # skip bones
        if child.name in bone_dict:
            continue
        # not a bone, so add it
        self.addChild(child)
        # fix links to skeleton root and bones
        for externalblock in child.tree():
            if isinstance(externalblock, self.cls.NiSkinInstance):
                if not(externalblock.skeletonRoot is skelroot):
                    raise ValueError(
                        "expected skeleton root %s but got %s"
                        % (skelroot.name, externalblock.skeletonRoot.name))
                externalblock.skeletonRoot = self
                for i, externalbone in enumerate(externalblock.bones):
                    externalblock.bones[i] = bone_dict[externalbone.name]

def sendGeometriesToBindPosition(self):
    """Call this on the skeleton root of geometries. This function will
    transform the geometries, such that all skin data transforms coincide, or
    at least coincide partially.

    @return: A number quantifying the remaining difference between bind
        positions.
    @rtype: C{float}
    """
    # get logger
    logger = logging.getLogger("pyffi.nif.ninode")
    # maps bone name to bind position transform matrix (relative to
    # skeleton root)
    skelroot = self
    bone_bind_transform = {}
    # find all skinned geometries with self as skeleton root
    geoms = [geom for geom in self.tree()
             if (isinstance(geom, self.cls.NiGeometry)
                 and geom.isSkin()
                 and geom.skinInstance.skeletonRoot is skelroot)]
    # sort geometries by bone level
    # this ensures that "parent" geometries serve as reference for "child"
    # geometries
    sorted_geoms = []
    for bone in self.tree():
        if not isinstance(bone, self.cls.NiNode):
            continue
        for geom in geoms:
            if not geom in sorted_geoms:
                if bone in geom.skinInstance.bones:
                    sorted_geoms.append(geom)
    geoms = sorted_geoms
    # now go over all geometries and synchronize their relative bind poses
    for geom in geoms:
        skininst = geom.skinInstance
        skindata = skininst.data
        # set difference matrix to identity
        diff = self.cls.Matrix44()
        diff.setIdentity()
        # go over all bones in current geometry, see if it has been visited
        # before
        for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
            if bonenode.name in bone_bind_transform:
                # calculate difference
                # (see explanation below)
                diff = (bonedata.getTransform()
                        * bone_bind_transform[bonenode.name]
                        * geom.getTransform(skelroot).getInverse())
                break

        if diff.isIdentity():
            logger.debug("%s is already in bind position" % geom.name)
        else:
            logger.info("fixing %s bind position" % geom.name)
            # explanation:
            # we must set the bonedata transform T' such that its bone bind
            # position matrix
            #   T'^-1 * G
            # (where T' = the updated bonedata.getTransform()
            # and G = geom.getTransform(skelroot))
            # coincides with the desired matrix
            #   B = bone_bind_transform[bonenode.name]
            # in other words:
            #   T' = G * B^-1
            # or, with diff = D = T * B * G^-1
            #   T' = D^-1 * T
            # to keep the geometry in sync, the vertices and normals must
            # be multiplied with D, e.g. v' = v * D
            # because the full transform
            #    v * T * ... = v * D * D^-1 * T * ... = v' * T' * ...
            # must be kept invariant
            for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
                logger.debug("transforming bind position of bone %s"
                             % bonenode.name)
                bonedata.setTransform(diff.getInverse()
                                      * bonedata.getTransform())
            # transform geometry
            logger.debug("transforming vertices and normals")
            for vert in geom.data.vertices:
                newvert = vert * diff
                vert.x = newvert.x
                vert.y = newvert.y
                vert.z = newvert.z
            for norm in geom.data.normals:
                newnorm = norm * diff.getMatrix33()
                norm.x = newnorm.x
                norm.y = newnorm.y
                norm.z = newnorm.z

        # store updated bind position for future reference
        for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
            bone_bind_transform[bonenode.name] = (
                bonedata.getTransform().getInverse()
                * geom.getTransform(skelroot))

    # validation: check that bones share bind position
    bone_bind_transform = {}
    error = 0.0
    for geom in geoms:
        skininst = geom.skinInstance
        skindata = skininst.data
        # go over all bones in current geometry, see if it has been visited
        # before
        for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
            if bonenode.name in bone_bind_transform:
                # calculate difference
                diff = ((bonedata.getTransform().getInverse()
                         * geom.getTransform(skelroot))
                        - bone_bind_transform[bonenode.name])
                # calculate error (sup norm)
                error = max(error,
                            max(max(abs(elem) for elem in row)
                                for row in diff.asList()))
            else:
                bone_bind_transform[bonenode.name] = (
                    bonedata.getTransform().getInverse()
                    * geom.getTransform(skelroot))

    logger.debug("Geometry bind position error is %f" % error)
    if error > 1e-3:
        logger.warning("Failed to send some geometries to bind position")
    return error

def sendBonesToBindPosition(self):
    """This function will send all bones of geometries of this skeleton root
    to their bind position. For best results, call
    L{sendGeometriesToBindPosition} first.

    @return: A number quantifying the remaining difference between bind
        positions.
    @rtype: C{float}
    """
    # get logger
    logger = logging.getLogger("pyffi.nif.ninode")
    # find all skinned geometries with self as skeleton root
    skelroot = self
    geoms = [geom for geom in self.tree()
             if (isinstance(geom, self.cls.NiGeometry)
                 and geom.isSkin()
                 and geom.skinInstance.skeletonRoot is skelroot)]

    # check all bones and bone datas to see if a bind position exists
    bonelist = []
    error = 0.0
    for geom in geoms:
        skininst = geom.skinInstance
        skindata = skininst.data
        for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
            # make sure all bone data of shared bones coincides
            for othergeom, otherbonenode, otherbonedata in bonelist:
                if bonenode is otherbonenode:
                    diff = ((otherbonedata.getTransform().getInverse()
                             *
                             othergeom.getTransform(skelroot))
                            -
                            (bonedata.getTransform().getInverse()
                             *
                             geom.getTransform(skelroot)))
                    if diff.supNorm() > 1e-3:
                        logger.warning("Geometries %s and %s do not share the same bind position: bone %s will be sent to a position matching only one of these" % (geom.name, othergeom.name, bonenode.name))
                    # break the loop
                    break
            else:
                # the loop did not break, so the bone was not yet added
                # add it now
                logger.debug("Found bind position data for %s" % bonenode.name)
                bonelist.append((geom, bonenode, bonedata))

    # numerical stability is a problem, therefore use two different algorithms:
    # - the first algorithm simply makes all transforms correct by changing
    # each local bone matrix in such a way that the global matrix relative to
    # the skeleton root matches the skinning information
    # - the second algorithm makes the local transforms correct by comparing
    # with relative skinning information (this is of course an incomplete
    # check, but it is good enough to fix numerical errors up the hierarchy)
    #
    # this approach seems to work well enough in practice

    logger.info("Repositioning bones - first pass")
    # reposition the bones: algorithm 1
    # this algorithm is numerically most stable if bones are traversed
    # in hierarchical order, so first sort the bones
    sorted_bonelist = []
    for node in skelroot.tree():
        if not isinstance(node, self.cls.NiNode):
            continue
        for geom, bonenode, bonedata in bonelist:
            if node is bonenode:
                sorted_bonelist.append((geom, bonenode, bonedata))
    bonelist = sorted_bonelist
    # now reposition the bones
    for geom, bonenode, bonedata in bonelist:
        # explanation:
        # v * CHILD * PARENT * ...
        # = v * CHILD * DIFF^-1 * DIFF * PARENT * ...
        # and now choose DIFF such that DIFF * PARENT * ... = desired transform

        # calculate desired transform relative to skeleton root
        # transform is DIFF * PARENT
        transform = (bonedata.getTransform().getInverse()
                     * geom.getTransform(skelroot))
        # calculate difference
        diff = transform * bonenode.getTransform(skelroot).getInverse()
        if not diff.isIdentity():
            logger.info("Sending %s to bind position"
                        % bonenode.name)
            # fix transform of this node
            bonenode.setTransform(diff * bonenode.getTransform())
            # fix transform of all its children
            diff_inv = diff.getInverse()
            for childnode in bonenode.children:
                if childnode:
                    childnode.setTransform(childnode.getTransform() * diff_inv)
        else:
            logger.debug("%s is already in bind position"
                         % bonenode.name)

    logger.info("Repositioning bones - second pass")
    # reposition the bones, using the relative transform method
    # (this is the old niflib method, also see
    # NiGeometry.sendBonesToBindPosition)
    # this method fixes numerical errors that tend to accumulate
    for parent_geom, parent_bonenode, parent_bonedata in bonelist:
        # calculate desired transform of parent, relative to skeleton root
        parent_transform = (parent_bonedata.getTransform().getInverse()
                            * parent_geom.getTransform(skelroot))
        # if parent is a child of the skeleton root, then fix its
        # transfrom
        if parent_bonenode in skelroot.children:
            if parent_bonenode.getTransform() != parent_transform:
                logger.info("Sending %s to bind position"
                            % parent_bonenode.name)
                parent_bonenode.setTransform(parent_transform)
            else:
                logger.debug("%s is already in bind position"
                             % parent_bonenode.name)
        # fix the transform of all its children
        for child_geom, child_bonenode, child_bonedata in bonelist:
            if child_bonenode in parent_bonenode.children:
                # calculate desired transform of child, relative to
                # skeleton root
                child_transform = (child_bonedata.getTransform().getInverse()
                                   * child_geom.getTransform(skelroot))
                # calculate transform relative to parent
                child_relative_transform = (child_transform
                                            * parent_transform.getInverse())
                if child_bonenode.getTransform() != child_relative_transform:
                    logger.debug("Sending %s to bind position"
                                 % child_bonenode.name)
                    child_bonenode.setTransform(child_relative_transform)
                else:
                    logger.debug("%s is already in bind position"
                                 % child_bonenode.name)

    # validate
    error = 0.0
    diff_error = 0.0
    for geom in geoms:
        skininst = geom.skinInstance
        skindata = skininst.data
        skelroot = self
        # calculate geometry transform
        geomtransform = geom.getTransform(skelroot)
        # check skin data fields (also see NiGeometry.updateBindPosition)
        for i, bone in enumerate(skininst.bones):
            diff = ((skindata.boneList[i].getTransform().getInverse()
                     * geomtransform)
                    - bone.getTransform(skelroot))
            # calculate error (sup norm)
            diff_error = max(max(abs(elem) for elem in row)
                             for row in diff.asList())
            if diff_error > 1e-3:
                logger.warning(
                    "Failed to set bind position of bone %s for geometry %s (error is %f)"
                    % (bone.name, geom.name, diff_error))
            error = max(error, diff_error)

    logger.debug("Bone bind position maximal error is %f" % error)
    if error > 1e-3:
        logger.warning("Failed to send some bones to bind position")
    return error
