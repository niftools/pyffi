"""Spells for optimizing nif files."""

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

from itertools import izip

from PyFFI.Formats.NIF import NifFormat
import PyFFI.utils.tristrip
import PyFFI.spells
import PyFFI.spells.NIF
import PyFFI.spells.NIF.fix

# set flag to overwrite files
__readonly__ = False

# example usage
__examples__ = """* Standard usage:

    python niftoaster.py optimize /path/to/copy/of/my/nifs

* Optimize, but do not merge NiMaterialProperty blocks:

    python niftoaster.py optimize --exclude=NiMaterialProperty /path/to/copy/of/my/nifs
"""

class SpellCleanRefLists(PyFFI.spells.NIF.NifSpell):
    """Remove empty and duplicate entries in reference lists."""

    SPELLNAME = "opt_cleanreflists"
    READONLY = False

    def datainspect(self):
        # see MadCat221's metstaff.nif:
        # merging data on PSysMeshEmitter affects particle system
        # so do not merge child links on this nif (probably we could still
        # merge other things: this is just a quick hack to make sure the
        # optimizer won't do anything wrong)
        try:
            if self.data.header.hasBlockType(NifFormat.NiPSysMeshEmitter):
                return False
        except ValueError:
            # when in doubt, assume it does not have this block
            pass
        # so far, only reference lists in NiObjectNET blocks, NiAVObject
        # blocks, and NiNode blocks are checked
        return self.inspectblocktype(NifFormat.NiObjectNET)

    def branchinspect(self, branch):
        # only inspect the NiObjectNET branch
        return isinstance(branch, NifFormat.NiObjectNET)

    def cleanreflist(self, reflist, category):
        """Return a cleaned copy of the given list of references."""
        # delete empty and duplicate references
        cleanlist = []
        for ref in reflist:
            if ref is None:
                self.toaster.msg("removing empty %s reference" % category)
            elif ref in cleanlist:
                self.toaster.msg("removing duplicate %s reference" % category)
            else:
                cleanlist.append(ref)
        # done
        return cleanlist

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiObjectNET):
            # clean extra data
            branch.setExtraDatas(
                self.cleanreflist(branch.getExtraDatas(), "extra"))
        if isinstance(branch, NifFormat.NiAVObject):
            # clean properties
            branch.setProperties(
                self.cleanreflist(branch.getProperties(), "property"))
        if isinstance(branch, NifFormat.NiNode):
            # clean children
            branch.setChildren(
                self.cleanreflist(branch.getChildren(), "child"))
            # clean effects
            branch.setEffects(
                self.cleanreflist(branch.getEffects(), "effect"))
        # always recurse further
        return True

class SpellMergeDuplicates(PyFFI.spells.NIF.NifSpell):
    """Remove duplicate branches."""

    SPELLNAME = "opt_mergeduplicates"
    READONLY = False

    def __init__(self, *args, **kwargs):
        PyFFI.spells.NIF.NifSpell.__init__(self, *args, **kwargs)
        # list of all branches visited so far
        self.branches = []

    def datainspect(self):
        # see MadCat221's metstaff.nif:
        # merging data on PSysMeshEmitter affects particle system
        # so do not merge shapes on this nif (probably we could still
        # merge other things: this is just a quick hack to make sure the
        # optimizer won't do anything wrong)
        try:
            return not self.data.header.hasBlockType(NifFormat.NiPSysMeshEmitter)
        except ValueError:
            # when in doubt, do the spell
            return True

    def branchinspect(self, branch):
        # only inspect the NiObjectNET branch (merging havok can mess up things)
        return isinstance(branch, (NifFormat.NiObjectNET,
                                   NifFormat.NiGeometryData))

    def branchentry(self, branch):
        for otherbranch in self.branches:
            if (branch is not otherbranch and
                branch.isInterchangeable(otherbranch)):
                # skip properties that have controllers (the
                # controller data cannot always be reliably checked,
                # see also issue #2106668)
                if (isinstance(branch, NifFormat.NiProperty)
                    and branch.controller):
                    continue
                # interchangeable branch found!
                self.toaster.msg("removing duplicate branch")
                self.data.replaceGlobalNode(branch, otherbranch)
                # branch has been replaced, so no need to recurse further
                return False
        else:
            # no duplicate found, add to list of visited branches
            self.branches.append(branch)
            # continue recursion
            return True

class SpellOptimizeGeometry(PyFFI.spells.NIF.NifSpell):
    """Optimize all geometries:
      - remove duplicate vertices
      - stripify if strips are long enough
      - recalculate skin partition
      - recalculate tangent space 
    """

    SPELLNAME = "opt_geometry"
    READONLY = False

    # spell parameters
    STRIPLENCUTOFF = 10
    STITCH = True

    def __init__(self, *args, **kwargs):
        PyFFI.spells.NIF.NifSpell.__init__(self, *args, **kwargs)
        # list of all optimized geometries so far
        # (to avoid optimizing the same geometry twice)
        self.optimized = []

    def datainspect(self):
        # so far, only reference lists in NiObjectNET blocks, NiAVObject
        # blocks, and NiNode blocks are checked
        return self.inspectblocktype(NifFormat.NiTriBasedGeom)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        """Optimize a NiTriStrips or NiTriShape block:
          - remove duplicate vertices
          - stripify if strips are long enough
          - recalculate skin partition
          - recalculate tangent space 

        @todo: Limit the length of strips (see operation optimization mod for
            Oblivion!)
        """
        if not isinstance(branch, NifFormat.NiTriBasedGeom):
            # keep recursing
            return True

        if branch in self.optimized:
            # already optimized
            return False
    
        # we found a geometry to optimize

        # cover degenerate case
        if branch.data.numVertices < 3:
            self.toaster.msg("less than 3 vertices: removing branch")
            self.data.replaceGlobalNode(branch, None)
            return False

        # shortcut
        data = branch.data

        self.toaster.msg("removing duplicate vertices")
        v_map = [0 for i in xrange(data.numVertices)] # maps old index to new index
        v_map_inverse = [] # inverse: map new index to old index
        k_map = {} # maps hash to new vertex index
        index = 0  # new vertex index for next vertex
        for i, vhash in enumerate(data.getVertexHashGenerator()):
            try:
                k = k_map[vhash]
            except KeyError:
                # vertex is new
                k_map[vhash] = index
                v_map[i] = index
                v_map_inverse.append(i)
                index += 1
            else:
                # vertex already exists
                v_map[i] = k
        del k_map

        new_numvertices = index
        self.toaster.msg("(num vertices was %i and is now %i)"
                         % (len(v_map), new_numvertices))
        # copy old data
        oldverts = [[v.x, v.y, v.z] for v in data.vertices]
        oldnorms = [[n.x, n.y, n.z] for n in data.normals]
        olduvs   = [[[uv.u, uv.v] for uv in uvset] for uvset in data.uvSets]
        oldvcols = [[c.r, c.g, c.b, c.a] for c in data.vertexColors]
        if branch.skinInstance: # for later
            oldweights = branch.getVertexWeights()
        # set new data
        data.numVertices = new_numvertices
        if data.hasVertices:
            data.vertices.updateSize()
        if data.hasNormals:
            data.normals.updateSize()
        data.uvSets.updateSize()
        if data.hasVertexColors:
            data.vertexColors.updateSize()
        for i, v in enumerate(data.vertices):
            old_i = v_map_inverse[i]
            v.x = oldverts[old_i][0]
            v.y = oldverts[old_i][1]
            v.z = oldverts[old_i][2]
        for i, n in enumerate(data.normals):
            old_i = v_map_inverse[i]
            n.x = oldnorms[old_i][0]
            n.y = oldnorms[old_i][1]
            n.z = oldnorms[old_i][2]
        for j, uvset in enumerate(data.uvSets):
            for i, uv in enumerate(uvset):
                old_i = v_map_inverse[i]
                uv.u = olduvs[j][old_i][0]
                uv.v = olduvs[j][old_i][1]
        for i, c in enumerate(data.vertexColors):
            old_i = v_map_inverse[i]
            c.r = oldvcols[old_i][0]
            c.g = oldvcols[old_i][1]
            c.b = oldvcols[old_i][2]
            c.a = oldvcols[old_i][3]
        del oldverts
        del oldnorms
        del olduvs
        del oldvcols

        # update vertex indices in strips/triangles
        if isinstance(branch, NifFormat.NiTriStrips):
            for strip in data.points:
                for i in xrange(len(strip)):
                    strip[i] = v_map[strip[i]]
        elif isinstance(branch, NifFormat.NiTriShape):
            for tri in data.triangles:
                tri.v1 = v_map[tri.v1]
                tri.v2 = v_map[tri.v2]
                tri.v3 = v_map[tri.v3]

        # stripify trishape/tristrip
        if isinstance(branch, NifFormat.NiTriStrips):
            self.toaster.msg("recalculating strips")
            origlen = sum(i for i in data.stripLengths)
            data.setTriangles(data.getTriangles())
            newlen = sum(i for i in data.stripLengths)
            self.toaster.msg("(strip length was %i and is now %i)"
                             % (origlen, newlen))
        elif isinstance(branch, NifFormat.NiTriShape):
            self.toaster.msg("stripifying")
            newbranch = branch.getInterchangeableTriStrips()
            self.data.replaceGlobalNode(branch, newbranch)
            branch = newbranch
            data = newbranch.data
        # average, weighed towards large strips
        if isinstance(branch, NifFormat.NiTriStrips):
            # note: the max(1, ...) is to avoid ZeroDivisionError
            avgstriplen = float(sum(i * i for i in data.stripLengths)) \
                / max(1, sum(i for i in data.stripLengths))
            self.toaster.msg("(average strip length is %f)" % avgstriplen)
            if avgstriplen < self.STRIPLENCUTOFF:
                self.toaster.msg("average strip length < %f so triangulating"
                                 % self.STRIPLENCUTOFF)
                newbranch = branch.getInterchangeableTriShape()
                self.data.replaceGlobalNode(branch, newbranch)
                branch = newbranch
                data = newbranch.data
            elif self.STITCH:
                self.toaster.msg("stitching strips (using %i stitches)"
                                 % len(data.getStrips()))
                data.setStrips([PyFFI.utils.tristrip.stitchStrips(data.getStrips())])

        # update skin data
        if branch.skinInstance:
            self.toaster.msg("update skin data vertex mapping")
            skindata = branch.skinInstance.data
            newweights = []
            for i in xrange(new_numvertices):
                newweights.append(oldweights[v_map_inverse[i]])
            for bonenum, bonedata in enumerate(skindata.boneList):
                w = []
                for i, weightlist in enumerate(newweights):
                    for bonenum_i, weight_i in weightlist:
                        if bonenum == bonenum_i:
                            w.append((i, weight_i))
                bonedata.numVertices = len(w)
                bonedata.vertexWeights.updateSize()
                for j, (i, weight_i) in enumerate(w):
                    bonedata.vertexWeights[j].index = i
                    bonedata.vertexWeights[j].weight = weight_i

            # update skin partition (only if branch already exists)
            branch._validateSkin()
            skininst = branch.skinInstance
            skinpart = skininst.skinPartition
            if not skinpart:
                skinpart = skininst.data.skinPartition

            if skinpart:
                self.toaster.msg("updating skin partition")
                # use Oblivion settings
                branch.updateSkinPartition(
                    maxbonesperpartition = 18, maxbonespervertex = 4,
                    stripify = True, verbose = 0)

        # update morph data
        for morphctrl in branch.getControllers():
            if isinstance(morphctrl, NifFormat.NiGeomMorpherController):
                morphdata = morphctrl.data
                # skip empty morph data
                if not morphdata:
                    continue
                # convert morphs
                self.toaster.msg("updating morphs")
                for morph in morphdata.morphs:
                    # store a copy of the old vectors
                    oldmorphvectors = [(vec.x, vec.y, vec.z)
                                       for vec in morph.vectors]
                    for old_i, vec in izip(v_map_inverse, morph.vectors):
                        vec.x = oldmorphvectors[old_i][0]
                        vec.y = oldmorphvectors[old_i][1]
                        vec.z = oldmorphvectors[old_i][2]
                    del oldmorphvectors
                # resize matrices
                morphdata.numVertices = new_numvertices
                for morph in morphdata.morphs:
                     morph.arg = morphdata.numVertices # manual argument passing
                     morph.vectors.updateSize()

        # recalculate tangent space (only if the branch already exists)
        if branch.find(block_name='Tangent space (binormal & tangent vectors)',
                       block_type=NifFormat.NiBinaryExtraData):
            self.toaster.msg("recalculating tangent space")
            branch.updateTangentSpace()

        # stop recursion
        return False

# XXX todo
class SpellSplitGeometry(PyFFI.spells.NIF.NifSpell):
    """Optimize geometry by splitting large models into pieces.
    (This spell is not yet fully implemented!)
    """
    SPELLNAME = "opt_split"
    READONLY = False
    THRESHOLD_RADIUS = 100 #: Threshold where to split geometry.

    # XXX todo
    @staticmethod
    def addVertex(sourceindex, v_map, sourcedata, destdata):
        """Add a vertex from source to destination. Returns index in
        destdata of the vertex."""
        # v_map maps source indices that have already been added to the
        # index they already have in the destdata

        # hasNormals, numUvSets, etc. of destdata must already match
        # the sourcedata
        try:
            return v_map[sourceindex]
        except KeyError:
            v_map[sourceindex] = destdata.numVertices
            destdata.numVertices += 1
            destdata.vertices.updateSize()
            destdata.vertices[-1].x = sourcedata.vertices[sourceindex].x
            destdata.vertices[-1].y = sourcedata.vertices[sourceindex].y
            destdata.vertices[-1].z = sourcedata.vertices[sourceindex].z
            if sourcedata.hasNormals:
                destdata.normals.updateSize()
                destdata.normals[-1].x = sourcedata.normals[sourceindex].x
                destdata.normals[-1].y = sourcedata.normals[sourceindex].y
                destdata.normals[-1].z = sourcedata.normals[sourceindex].z
            if sourcedata.hasVertexColors:
                destdata.vertexColors.updateSize()
                destdata.vertexColors[-1].r = sourcedata.vertexColors[sourceindex].r
                destdata.vertexColors[-1].g = sourcedata.vertexColors[sourceindex].g
                destdata.vertexColors[-1].b = sourcedata.vertexColors[sourceindex].b
                destdata.vertexColors[-1].a = sourcedata.vertexColors[sourceindex].a
            if sourcedata.hasUv:
                for sourceuvset, destuvset in izip(sourcedata.uvSets, destdata.uvSets):
                    destuvset.updateSize()
                    destuvset[-1].u = sourceuvset[sourceindex].u
                    destuvset[-1].v = sourceuvset[sourceindex].v
            return destdata.numVertices

    # XXX todo
    @staticmethod
    def addTriangle(sourcetriangle, v_map, sourcedata, destdata):
        """Add a triangle from source to destination."""
        desttriangle = [
            destdata.addVertex(sourceindex)
            for sourceindex in sourcetriangle]
        destdata.numTriangles += 1
        destdata.triangles.updateSize()
        destdata.triangles[-1].v1 = desttriangle[0]
        destdata.triangles[-1].v2 = desttriangle[0]
        destdata.triangles[-1].v3 = desttriangle[0]

    # XXX todo
    @staticmethod
    def getSize(vertices, triangle):
        """Calculate size of geometry data + given triangle."""
        def helper(oper, coord):
            return oper((getattr(vert, coord) for vert in triangle),
                        oper(getattr(vert, coord) for vert in vertices))
        minx = helper(min, "x")
        miny = helper(min, "y")
        minz = helper(min, "z")
        maxx = helper(max, "x")
        maxy = helper(max, "y")
        maxz = helper(max, "z")
        return max((maxx - minx, maxy - miny, maxz - minz))

    # XXX todo: merge into branchentry spell
    @staticmethod
    def split(geom, threshold_radius = THRESHOLD_RADIUS):
        """Takes a NiGeometry block and splits the geometries. Returns a NiNode
        which contains the splitted geometry. Note that everything is triangulated
        in the process."""
        # make list of triangles
        # this will be used as the list of triangles still to add
        triangles = geom.data.getTriangles()
        node = NifFormat.NiNode().deepcopy(
            NifFormat.NiAVObject.deepcopy(geom))
        geomsplit = None
        # while there are still triangles to add...
        while triangles:
            if geomsplit is None:
                # split new geometry
                geomsplit = NifFormat.NiTriShape()
                node.addChild(geomsplit)
                geomsplit.data = NifFormat.NiTriShapeData()
                v_map = {}
                # copy relevant data
                geomsplit.name = "%s:%i" % (geom.name, node.numChildren - 1)
                geomsplit.data.hasVertices = geom.data.hasVertices
                geomsplit.data.hasNormals = geom.data.hasNormals
                geomsplit.data.hasVertexColors = geom.data.hasVertexColors
                geomsplit.data.numUvSets = geom.data.numUvSets
                geomsplit.data.hasUv = geom.data.hasUv
                geomsplit.data.uvSets.updateSize()
                # assign it a random triangle
                triangle = triangles.pop(0)
                addTriangle(triangle, v_map, geom.data, geomsplit.data)
            # find face that is close to current geometry
            for triangle in triangles:
                 if getSize(geomsplit.data,
                            tuple(geom.data.vertices[index]
                                  for index in triangle)) < threshold_radius:
                     addTriangle(triangle, v_map, geom.data, geomsplit.data)
                     break
            else:
                # if exceeded, start new geometry
                # first finish some things in geomsplit data
                geomsplit.data.updateCenterRadius()
                # setting geomsplit to None flags this for
                # the next iteration
                geomsplit = None
        # return grouping node
        return node

    def __init__(self, *args, **kwargs):
        PyFFI.spells.NIF.NifSpell.__init__(self, *args, **kwargs)
        # list of all optimized geometries so far
        # (to avoid optimizing the same geometry twice)
        self.optimized = []

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiTriBasedGeom)

    def branchinspect(self, branch):
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if not isinstance(branch, NifFormat.NiTriBasedGeom):
            # keep recursing
            return True

        if branch in self.optimized:
            # already optimized
            return False
    
        # we found a geometry to optimize
        # XXX todo
        # get geometry data
        geomdata = block.data
        if not geomdata:
            self.optimized.append(block)
            return False
        # check radius
        if geomdata.radius < self.THRESHOLD_RADIUS:
            optimized_geometries.append(block)
            return False
        # radius is over the threshold, so re-organize the geometry
        newblock = split(block, threshold_radius = THRESHOLD_RADIUS)
        # TODO replace block with newblock everywhere (write dedicated
        #      function in PyFFI for replacement)
        data.replaceGlobalNode(block, newblock)

        self.optimized.append(block)

        # stop recursing
        return False

class SpellOptimize(
    PyFFI.spells.SpellGroupSeries(
        PyFFI.spells.SpellGroupParallel(
            SpellCleanRefLists,
            PyFFI.spells.NIF.fix.SpellDetachHavokTriStripsData,
            PyFFI.spells.NIF.fix.SpellFixTexturePath,
            PyFFI.spells.NIF.fix.SpellClampMaterialAlpha),
        SpellMergeDuplicates,
        SpellOptimizeGeometry)):
    """Global fixer and optimizer spell."""
    SPELLNAME = "optimize"

