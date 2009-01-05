"""Custom functions for NiTriBasedGeom."""

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

import struct
from itertools import izip

from PyFFI.Utils import TriStrip

def updateTangentSpace(self, as_extra=True):
    """Recalculate tangent space data.

    @param as_extra: Whether to store the tangent space data as extra data
        (as in Oblivion) or not (as in Fallout 3).
    """
    # check that self.data exists and is valid
    if not isinstance(self.data, self.cls.NiTriBasedGeomData):
        raise ValueError(
            'cannot update tangent space of a geometry with %s data'
            %(self.data.__class__ if self.data else 'no'))

    verts = self.data.vertices
    norms = self.data.normals
    if len(self.data.uvSets) > 0:
        uvs   = self.data.uvSets[0]
    else:
        return # no uv sets so no tangent space

    # check that shape has norms and uvs
    if len(uvs) == 0 or len(norms) == 0: return

    bin = []
    tan = []
    for i in xrange(self.data.numVertices):
        bin.append(self.cls.Vector3())
        tan.append(self.cls.Vector3())

    # calculate tangents and binormals from vertex and texture coordinates
    for t1, t2, t3 in self.data.getTriangles():
        # skip degenerate triangles
        if t1 == t2 or t2 == t3 or t3 == t1: continue

        v1 = verts[t1]
        v2 = verts[t2]
        v3 = verts[t3]
        w1 = uvs[t1]
        w2 = uvs[t2]
        w3 = uvs[t3]
        v2v1 = v2 - v1
        v3v1 = v3 - v1
        w2w1 = w2 - w1
        w3w1 = w3 - w1

        # surface of triangle in texture space
        r = w2w1.u * w3w1.v - w3w1.u * w2w1.v

        # sign of surface
        r_sign = (1 if r >= 0 else -1)

        # contribution of this triangle to tangents and binormals
        sdir = self.cls.Vector3()
        sdir.x = w3w1.v * v2v1.x - w2w1.v * v3v1.x
        sdir.y = w3w1.v * v2v1.y - w2w1.v * v3v1.y
        sdir.z = w3w1.v * v2v1.z - w2w1.v * v3v1.z
        sdir *= r_sign
        try:
            sdir.normalize()
        except ZeroDivisionError: # catches zero vector
            continue # skip triangle
        except ValueError: # catches invalid data
            continue # skip triangle

        tdir = self.cls.Vector3()
        tdir.x = w2w1.u * v3v1.x - w3w1.u * v2v1.x
        tdir.y = w2w1.u * v3v1.y - w3w1.u * v2v1.y
        tdir.z = w2w1.u * v3v1.z - w3w1.u * v2v1.z
        tdir *= r_sign
        try:
            tdir.normalize()
        except ZeroDivisionError: # catches zero vector
            continue # skip triangle
        except ValueError: # catches invalid data
            continue # skip triangle

        # vector combination algorithm could possibly be improved
        for i in [t1, t2, t3]:
            tan[i] += tdir
            bin[i] += sdir

    xvec = self.cls.Vector3()
    xvec.x = 1.0
    xvec.y = 0.0
    xvec.z = 0.0
    yvec = self.cls.Vector3()
    yvec.x = 0.0
    yvec.y = 1.0
    yvec.z = 0.0
    for i in xrange(self.data.numVertices):
        n = norms[i]
        try:
            n.normalize()
        except (ValueError, ZeroDivisionError):
            # this happens if the normal has NAN values or is zero
            # just pick something in that case
            n = yvec
        try:
            # turn n, bin, tan into a base via Gram-Schmidt
            bin[i] -= n * (n * bin[i])
            bin[i].normalize()
            tan[i] -= n * (n * tan[i])
            tan[i] -= bin[i] * (bin[i] * tan[i])
            tan[i].normalize()
        except ZeroDivisionError:
            # insuffient data to set tangent space for this vertex
            # in that case pick a space
            bin[i] = xvec.crossproduct(n)
            try:
                bin[i].normalize()
            except ZeroDivisionError:
                bin[i] = yvec.crossproduct(n)
                bin[i].normalize() # should work now
            tan[i] = n.crossproduct(bin[i])

    if as_extra:
        # if tangent space extra data already exists, use it
        for block in self.getRefs():
            if isinstance(block, self.cls.NiBinaryExtraData):
                if block.name == 'Tangent space (binormal & tangent vectors)':
                    break
        else:
        # otherwise, create a new block and link it
            block = self.cls.NiBinaryExtraData()
            block.name = 'Tangent space (binormal & tangent vectors)'
            self.addExtraData(block)

        # write the data
        binarydata = ""
        for vec in tan + bin:
            binarydata += struct.pack('<fff', vec.x, vec.y, vec.z)
        block.binaryData = binarydata
    else:
        # set tangent space flag
        self.data.numUvSets |= 61440
        self.data.bsNumUvSets |= 61440
        self.data.tangents.updateSize()
        self.data.bitangents.updateSize()
        for vec, data_tan in izip(tan, self.data.tangents):
            data_tan.x = vec.x
            data_tan.y = vec.y
            data_tan.z = vec.z
        for vec, data_bitan in izip(bin, self.data.bitangents):
            data_bitan.x = vec.x
            data_bitan.y = vec.y
            data_bitan.z = vec.z

# ported from nifskope/skeleton.cpp:spSkinPartition
def updateSkinPartition(self,
                        maxbonesperpartition = 4, maxbonespervertex = 4,
                        verbose = 0, stripify = True, stitchstrips = False,
                        padbones = False):
    """Recalculate skin partition data.

    @param maxbonesperpartition: Maximum number of bones in each partition.
        The numBones field will not exceed this number.
    @param maxbonespervertex: Maximum number of bones per vertex.
        The numWeightsPerVertex field will be exactly equal to this number.
    @param verbose: Set verbosity level (0 = completely quiet).
    @param stripify: If true, stripify the partitions, otherwise use triangles.
    @param stitchstrips: If stripify is true, then set this to true to stitch
        the strips.
    @param padbones: Enforces the numbones field to be equal to
        maxbonesperpartition. Also ensures that the bone indices are unique
        and sorted, per vertex. Raises an exception if maxbonespervertex
        is not equal to maxbonesperpartition (in that case bone indices cannot
        be unique and sorted). This options is required for Freedom Force vs.
        the 3rd Reich skin partitions."""
    # shortcuts relevant blocks
    if not self.skinInstance: return # no skin, nothing to do
    self._validateSkin()
    geomdata = self.data
    skininst = self.skinInstance
    skindata = skininst.data

    # get skindata vertex weights
    if verbose: print "getting vertex weights"
    weights = self.getVertexWeights()

    # count minimum and maximum number of bones per vertex
    if verbose: print "counting min and max bones per vertex",
    minbones = min(len(weight) for weight in weights)
    maxbones = max(len(weight) for weight in weights)
    if minbones <= 0:
        raise ValueError('bad NiSkinData: some vertices have no weights')
    if verbose:
        print "   min", minbones, "   max", maxbones

    # reduce bone influences to meet maximum number of bones per vertex
    if verbose:
        print "imposing max bones per vertex", maxbonespervertex
    lostweight = 0.0
    for weight in weights:
        if len(weight) > maxbonespervertex:
            # delete bone influences with least weight
            weight.sort(key=lambda x: x[1], reverse=True) # sort by weight
            # save lost weight to return to user
            lostweight = max(
                lostweight, max(
                    [x[1] for x in weight[maxbonespervertex:]]))
            del weight[maxbonespervertex:] # only keep first elements
            # normalize
            totalweight = sum([x[1] for x in weight]) # sum of all weights
            for x in weight: x[1] /= totalweight
            maxbones = maxbonespervertex
        # sort by again by bone (relied on later when matching vertices)
        weight.sort(key=lambda x: x[0])

    # reduce bone influences to meet maximum number of bones per partition
    # (i.e. maximum number of bones per triangle)
    if verbose: print "imposing max bones per partition", maxbonesperpartition

    triangles = geomdata.getTriangles()

    for tri in triangles:
        while True:
            # find the bones influencing this triangle
            tribones = []
            for t in tri:
                tribones.extend([bonenum for bonenum, boneweight in weights[t]])
            tribones = set(tribones)
            # target met?
            if len(tribones) <= maxbonesperpartition: break
            # no, need to remove a bone

            # sum weights for each bone to find the one that least influences
            # this triangle
            tribonesweights = {}
            for bonenum in tribones: tribonesweights[bonenum] = 0.0
            nono = set() # bones with weight 1 cannot be removed
            for skinweights in [weights[t] for t in tri]:
                # skinweights[0] is the first skinweight influencing vertex t
                # and skinweights[0][0] is the bone number of that bone
                if len(skinweights) == 1: nono.add(skinweights[0][0])
                for bonenum, boneweight in skinweights:
                    tribonesweights[bonenum] += boneweight

            # select a bone to remove
            # first find bones we can remove

            # restrict to bones not in the nono set
            tribonesweights = [
                x for x in tribonesweights.items() if x[0] not in nono]
            if not tribonesweights:
                raise ValueError('cannot remove anymore bones in this skin; \
increase maxbonesperpartition and try again')
            # sort by vertex weight sum the last element of this list is now a
            # candidate for removal
            tribonesweights.sort(key=lambda x: x[1], reverse=True)
            minbone = tribonesweights[-1][0]

            # remove minbone from all vertices of this triangle and from all
            # matching vertices
            for t in tri:
                for tt in [t]: #match[t]:
                    # remove bone
                    weight = weights[tt]
                    for i, (bonenum, boneweight) in enumerate(weight):
                        if bonenum == minbone:
                            # save lost weight to return to user
                            lostweight = max(lostweight, boneweight)
                            del weight[i]
                            break
                    else:
                        continue
                    # normalize
                    totalweight = sum([x[1] for x in weight])
                    for x in weight: x[1] /= totalweight

    # split triangles into partitions
    if verbose: print "creating partitions"
    parts = []
    # keep creating partitions as long as there are triangles left
    while triangles:
        # create a partition
        part = [set(), []] # bones, triangles
        usedverts = set()
        addtriangles = True
        # keep adding triangles to it as long as the flag is set
        while addtriangles:
            # newtriangles is a list of triangles that have not been added to
            # the partition
            newtriangles = []
            for tri in triangles:
                # find the bones influencing this triangle
                tribones = []
                for t in tri:
                    tribones.extend([
                        bonenum for bonenum, boneweight in weights[t]])
                tribones = set(tribones)
                # if part has no bones, or if part has all bones of tribones
                # then add this triangle to this part
                if (not part[0]) or (part[0] >= tribones):
                    part[0] |= tribones
                    part[1].append(tri)
                    usedverts |= set(tri)
                else:
                    newtriangles.append(tri)
            triangles = newtriangles

            # if we have room left in the partition
            # then add an adjacent triangle
            addtriangles = False
            newtriangles = []
            if len(part[0]) < maxbonesperpartition:
                for tri in triangles:
                    if usedverts & set(tri):
                        # find the bones influencing this triangle
                        tribones = []
                        for t in tri:
                            tribones.extend([
                                bonenum for bonenum, boneweight in weights[t]])
                        tribones = set(tribones)
                        # and check if we exceed the maximum number of allowed
                        # bones
                        if len(part[0] | tribones) <= maxbonesperpartition:
                            part[0] |= tribones
                            part[1].append(tri)
                            usedverts |= set(tri)
                            # signal another try in adding triangles to
                            # the partition
                            addtriangles = True
                        else:
                            newtriangles.append(tri)
                    else:
                        newtriangles.append(tri)
                triangles = newtriangles

        parts.append(part)

    # merge all partitions
    if verbose: print "merging partitions"
    merged = True # signals success, in which case do another run
    while merged:
        merged = False
        # newparts is to contain the updated merged partitions as we go
        newparts = []
        # addedparts is the set of all partitions from parts that have been
        # added to newparts
        addedparts = set()
        # try all combinations
        for a, parta in enumerate(parts):
            if a in addedparts: continue
            newparts.append(parta)
            addedparts.add(a)
            for b, partb in enumerate(parts):
                if b <= a: continue
                if b in addedparts: continue
                if len(parta[0] | partb[0]) <= maxbonesperpartition:
                    parta[0] |= partb[0]
                    parta[1] += partb[1]
                    addedparts.add(b)
                    merged = True # signal another try in merging partitions
        # update partitions to the merged partitions
        parts = newparts

    # write the NiSkinPartition
    if verbose:
        print "creating NiSkinPartition with %i partitions" % len(parts)

    # if skin partition already exists, use it
    if skindata.skinPartition != None:
        skinpart = skindata.skinPartition
        skininst.skinPartition = skinpart
    elif skininst.skinPartition != None:
        skinpart = skininst.skinPartition
        skindata.skinPartition = skinpart
    else:
    # otherwise, create a new block and link it
        skinpart = self.cls.NiSkinPartition()
        skindata.skinPartition = skinpart
        skininst.skinPartition = skinpart

    # set number of partitions
    skinpart.numSkinPartitionBlocks = len(parts)
    skinpart.skinPartitionBlocks.updateSize()

    for skinpartblock, part in zip(skinpart.skinPartitionBlocks, parts):
        # get sorted list of bones
        bones = sorted(list(part[0]))
        triangles = part[1]
        # get sorted list of vertices
        vertices = set()
        for tri in triangles: vertices |= set(tri)
        vertices = sorted(list(vertices))
        # remap the vertices
        parttriangles = []
        for tri in triangles:
            parttriangles.append([vertices.index(t) for t in tri])
        if stripify:
            # stripify the triangles
            if verbose: print "  stripifying partition", parts.index(part)
            strips = TriStrip.stripify(
                parttriangles, stitchstrips = stitchstrips)
            numtriangles = 0
            for strip in strips: numtriangles += len(strip) - 2
        else:
            numtriangles = len(parttriangles)

        # set all the data
        skinpartblock.numVertices = len(vertices)
        skinpartblock.numTriangles = numtriangles
        if not padbones:
            skinpartblock.numBones = len(bones)
        else:
            if maxbonesperpartition != maxbonespervertex:
                raise ValueError(
                    'when padding bones maxbonesperpartition must be equal to \
maxbonespervertex')
            # freedom force vs. the 3rd reich needs exactly 4 bones per
            # partition on every partition block
            skinpartblock.numBones = maxbonesperpartition
        if stripify:
            skinpartblock.numStrips = len(strips)
        else:
            skinpartblock.numStrips = 0
        # maxbones would be enough as numWeightsPerVertex but the Gamebryo
        # engine doesn't like that, it seems to want exactly 4 even if there
        # are fewer
        skinpartblock.numWeightsPerVertex = maxbonespervertex
        skinpartblock.bones.updateSize()
        for i, bonenum in enumerate(bones):
            skinpartblock.bones[i] = bonenum
        for i in xrange(len(bones), skinpartblock.numBones):
            skinpartblock.bones[i] = 0 # dummy bone slots refer to first bone
        skinpartblock.hasVertexMap = True
        skinpartblock.vertexMap.updateSize()
        for i, v in enumerate(vertices):
            skinpartblock.vertexMap[i] = v
        skinpartblock.hasVertexWeights = True
        skinpartblock.vertexWeights.updateSize()
        for i, v in enumerate(vertices):
            for j in xrange(skinpartblock.numWeightsPerVertex):
                if j < len(weights[v]):
                    skinpartblock.vertexWeights[i][j] = weights[v][j][1]
                else:
                    skinpartblock.vertexWeights[i][j] = 0.0
        if stripify:
            skinpartblock.hasFaces = True
            skinpartblock.stripLengths.updateSize()
            for i, strip in enumerate(strips):
                skinpartblock.stripLengths[i] = len(strip)
            skinpartblock.strips.updateSize()
            for i, strip in enumerate(strips):
                for j, v in enumerate(strip):
                    skinpartblock.strips[i][j] = v
        else:
            skinpartblock.hasFaces = True
            # clear strip lengths array
            skinpartblock.stripLengths.updateSize()
            # clear strips array
            skinpartblock.strips.updateSize()
            skinpartblock.triangles.updateSize()
            for i, (v1,v2,v3) in enumerate(parttriangles):
                skinpartblock.triangles[i].v1 = v1
                skinpartblock.triangles[i].v2 = v2
                skinpartblock.triangles[i].v3 = v3
        skinpartblock.hasBoneIndices = True
        skinpartblock.boneIndices.updateSize()
        for i, v in enumerate(vertices):
            # the boneindices set keeps track of indices that have not been
            # used yet
            boneindices = set(range(skinpartblock.numBones))
            for j in xrange(len(weights[v])):
                skinpartblock.boneIndices[i][j] = bones.index(weights[v][j][0])
                boneindices.remove(skinpartblock.boneIndices[i][j])
            for j in xrange(len(weights[v]),skinpartblock.numWeightsPerVertex):
                if padbones:
                    # if padbones is True then we have enforced
                    # numBones == numWeightsPerVertex so this will not trigger
                    # a KeyError
                    skinpartblock.boneIndices[i][j] = boneindices.pop()
                else:
                    skinpartblock.boneIndices[i][j] = 0

        # sort weights by bone index (for ffvt3r)
        if padbones:
            for i, v in enumerate(vertices):
                vweights = []
                for j in xrange(skinpartblock.numWeightsPerVertex):
                    vweights.append([
                        skinpartblock.boneIndices[i][j],
                        skinpartblock.vertexWeights[i][j]])
                vweights.sort(key = lambda w: w[0])
                for j in xrange(skinpartblock.numWeightsPerVertex):
                    skinpartblock.boneIndices[i][j] = vweights[j][0]
                    skinpartblock.vertexWeights[i][j] = vweights[j][1]

    return lostweight

# ported from nifskope/skeleton.cpp:spFixBoneBounds
def updateSkinCenterRadius(self):
    """Update centers and radii of all skin data fields."""
    # shortcuts relevant blocks
    if not self.skinInstance:
        return # no skin, nothing to do
    self._validateSkin()
    geomdata = self.data
    skininst = self.skinInstance
    skindata = skininst.data

    verts = geomdata.vertices

    for skindatablock in skindata.boneList:
        # find all vertices influenced by this bone
        boneverts = [verts[skinweight.index]
                     for skinweight in skindatablock.vertexWeights]

        # find bounding box of these vertices
        low = self.cls.Vector3()
        low.x = min(v.x for v in boneverts)
        low.y = min(v.y for v in boneverts)
        low.z = min(v.z for v in boneverts)

        high = self.cls.Vector3()
        high.x = max(v.x for v in boneverts)
        high.y = max(v.y for v in boneverts)
        high.z = max(v.z for v in boneverts)

        # center is in the center of the bounding box
        center = (low + high) * 0.5

        # radius is the largest distance from the center
        r2 = 0.0
        for v in boneverts:
            d = center - v
            r2 = max(r2, d.x*d.x+d.y*d.y+d.z*d.z)
        radius = r2 ** 0.5

        # transform center in proper coordinates (radius remains unaffected)
        center *= skindatablock.getTransform()

        # save data
        skindatablock.boundingSphereOffset.x = center.x
        skindatablock.boundingSphereOffset.y = center.y
        skindatablock.boundingSphereOffset.z = center.z
        skindatablock.boundingSphereRadius = radius

def getInterchangeableTriShape(self):
    """Returns a NiTriShape block that is geometrically interchangeable."""
    # copy the shape (first to NiTriBasedGeom and then to NiTriShape)
    shape = self.cls.NiTriShape().deepcopy(
        self.cls.NiTriBasedGeom().deepcopy(self))
    # copy the geometry without strips
    shapedata = self.cls.NiTriShapeData().deepcopy(
        self.cls.NiTriBasedGeomData().deepcopy(self.data))
    # update the shape data
    shapedata.setTriangles(self.data.getTriangles())
    # relink the shape data
    shape.data = shapedata
    # and return the result
    return shape

def getInterchangeableTriStrips(self):
    """Returns a NiTriStrips block that is geometrically interchangeable."""
    # copy the shape (first to NiTriBasedGeom and then to NiTriStrips)
    strips = self.cls.NiTriStrips().deepcopy(
        self.cls.NiTriBasedGeom().deepcopy(self))
    # copy the geometry without triangles
    stripsdata = self.cls.NiTriStripsData().deepcopy(
        self.cls.NiTriBasedGeomData().deepcopy(self.data))
    # update the shape data
    stripsdata.setTriangles(self.data.getTriangles())
    # relink the shape data
    strips.data = stripsdata
    # and return the result
    return strips
