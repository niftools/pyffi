"""Spells for optimizing nif files.

.. autoclass:: SpellCleanRefLists
   :show-inheritance:
   :members:

.. autoclass:: SpellMergeDuplicates
   :show-inheritance:
   :members:

.. autoclass:: SpellOptimizeGeometry
   :show-inheritance:
   :members:

.. autoclass:: SpellOptimize
   :show-inheritance:
   :members:

.. autoclass:: SpellDelUnusedBones
   :show-inheritance:
   :members:

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

from itertools import izip
import os.path # exists

from pyffi.formats.nif import NifFormat
import pyffi.utils.tristrip
import pyffi.spells
import pyffi.spells.nif
import pyffi.spells.nif.fix

# set flag to overwrite files
__readonly__ = False

# example usage
__examples__ = """* Standard usage:

    python niftoaster.py optimize /path/to/copy/of/my/nifs

* Optimize, but do not merge NiMaterialProperty blocks:

    python niftoaster.py optimize --exclude=NiMaterialProperty /path/to/copy/of/my/nifs
"""

class SpellCleanRefLists(pyffi.spells.nif.NifSpell):
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
            if self.data.header.has_block_type(NifFormat.NiPSysMeshEmitter):
                return False
        except ValueError:
            # when in doubt, assume it does not have this block
            pass
        # so far, only reference lists in NiObjectNET blocks, NiAVObject
        # blocks, and NiNode blocks are checked
        return self.inspectblocktype(NifFormat.NiObjectNET)

    def dataentry(self):
        self.data.roots = self.cleanreflist(self.data.roots, "root")
        return True

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
                self.changed = True
            elif ref in cleanlist:
                self.toaster.msg("removing duplicate %s reference" % category)
                self.changed = True
            else:
                cleanlist.append(ref)
        # done
        return cleanlist

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiObjectNET):
            # clean extra data
            branch.set_extra_datas(
                self.cleanreflist(branch.get_extra_datas(), "extra"))
        if isinstance(branch, NifFormat.NiAVObject):
            # clean properties
            branch.set_properties(
                self.cleanreflist(branch.get_properties(), "property"))
        if isinstance(branch, NifFormat.NiNode):
            # clean children
            branch.set_children(
                self.cleanreflist(branch.get_children(), "child"))
            # clean effects
            branch.set_effects(
                self.cleanreflist(branch.get_effects(), "effect"))
        # always recurse further
        return True

class SpellMergeDuplicates(pyffi.spells.nif.NifSpell):
    """Remove duplicate branches."""

    SPELLNAME = "opt_mergeduplicates"
    READONLY = False

    def __init__(self, *args, **kwargs):
        pyffi.spells.nif.NifSpell.__init__(self, *args, **kwargs)
        # list of all branches visited so far
        self.branches = []

    def datainspect(self):
        # see MadCat221's metstaff.nif:
        # merging data on PSysMeshEmitter affects particle system
        # so do not merge shapes on this nif (probably we could still
        # merge other things: this is just a quick hack to make sure the
        # optimizer won't do anything wrong)
        try:
            return not self.data.header.has_block_type(
                NifFormat.NiPSysMeshEmitter)
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
                branch.is_interchangeable(otherbranch)):
                # skip properties that have controllers (the
                # controller data cannot always be reliably checked,
                # see also issue #2106668)
                if (isinstance(branch, NifFormat.NiProperty)
                    and branch.controller):
                    continue
                # interchangeable branch found!
                self.toaster.msg("removing duplicate branch")
                self.data.replace_global_node(branch, otherbranch)
                self.changed = True
                # branch has been replaced, so no need to recurse further
                return False
        else:
            # no duplicate found, add to list of visited branches
            self.branches.append(branch)
            # continue recursion
            return True

class SpellOptimizeGeometry(pyffi.spells.nif.NifSpell):
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
        pyffi.spells.nif.NifSpell.__init__(self, *args, **kwargs)
        # list of all optimized geometries so far
        # (to avoid optimizing the same geometry twice)
        self.optimized = []

    def datainspect(self):
        # do not optimize if an egm or tri file is detected
        filename = self.stream.name
        if (os.path.exists(filename[:-3] + "egm")
            or os.path.exists(filename[:-3] + "tri")):
            return False
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

        # we're going to change the data
        self.changed = True

        # cover degenerate case
        if branch.data.num_vertices < 3:
            self.toaster.msg("less than 3 vertices: removing branch")
            self.data.replace_global_node(branch, None)
            return False

        # shortcut
        data = branch.data

        self.toaster.msg("removing duplicate vertices")
        v_map = [0 for i in xrange(data.num_vertices)] # maps old index to new index
        v_map_inverse = [] # inverse: map new index to old index
        k_map = {} # maps hash to new vertex index
        index = 0  # new vertex index for next vertex
        for i, vhash in enumerate(data.get_vertex_hash_generator()):
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
        olduvs   = [[[uv.u, uv.v] for uv in uvset] for uvset in data.uv_sets]
        oldvcols = [[c.r, c.g, c.b, c.a] for c in data.vertex_colors]
        if branch.skin_instance: # for later
            oldweights = branch.get_vertex_weights()
        # set new data
        data.num_vertices = new_numvertices
        if data.has_vertices:
            data.vertices.update_size()
            for i, v in enumerate(data.vertices):
                old_i = v_map_inverse[i]
                v.x = oldverts[old_i][0]
                v.y = oldverts[old_i][1]
                v.z = oldverts[old_i][2]
        if data.has_normals:
            data.normals.update_size()
            for i, n in enumerate(data.normals):
                old_i = v_map_inverse[i]
                n.x = oldnorms[old_i][0]
                n.y = oldnorms[old_i][1]
                n.z = oldnorms[old_i][2]
        # XXX todo: if ...has_uv_sets...:
        data.uv_sets.update_size()
        for j, uvset in enumerate(data.uv_sets):
            for i, uv in enumerate(uvset):
                old_i = v_map_inverse[i]
                uv.u = olduvs[j][old_i][0]
                uv.v = olduvs[j][old_i][1]
        if data.has_vertex_colors:
            data.vertex_colors.update_size()
            for i, c in enumerate(data.vertex_colors):
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
        if isinstance(data, NifFormat.NiTriStripsData):
            for strip in data.points:
                for i in xrange(len(strip)):
                    try:
                        strip[i] = v_map[strip[i]]
                    except IndexError:
                        self.toaster.logger.warn(
                            "Corrupt nif: bad vertex index in strip (%i); "
                            "replacing by valid index which might "
                            "modify your geometry!" % strip[i])
                        if i > 0:
                            strip[i] = strip[i-1]
                        else:
                            strip[i] = strip[i+1]
        elif isinstance(data, NifFormat.NiTriShapeData):
            for tri in data.triangles:
                tri.v_1 = v_map[tri.v_1]
                tri.v_2 = v_map[tri.v_2]
                tri.v_3 = v_map[tri.v_3]

        # stripify trishape/tristrip
        if data.num_triangles > 32000:
            self.toaster.logger.warn(
                "Found an insane amount of %i triangles in geometry: "
                "consider simplifying the mesh "
                "or breaking it up in smaller parts."
                % data.num_triangles)
        else:
            if isinstance(data, NifFormat.NiTriStripsData):
                self.toaster.msg("recalculating strips")
                origlen = sum(i for i in data.strip_lengths)
                data.set_triangles(data.get_triangles())
                newlen = sum(i for i in data.strip_lengths)
                self.toaster.msg("(strip length was %i and is now %i)"
                                 % (origlen, newlen))
            elif isinstance(data, NifFormat.NiTriShapeData):
                self.toaster.msg("stripifying")
                newbranch = branch.get_interchangeable_tri_strips()
                self.data.replace_global_node(branch, newbranch)
                branch = newbranch
                data = newbranch.data
            # average, weighed towards large strips
            if isinstance(data, NifFormat.NiTriStripsData):
                # note: the max(1, ...) is to avoid ZeroDivisionError
                avgstriplen = float(sum(i * i for i in data.strip_lengths)) \
                    / max(1, sum(i for i in data.strip_lengths))
                self.toaster.msg("(average strip length is %f)" % avgstriplen)
                if avgstriplen < self.STRIPLENCUTOFF:
                    self.toaster.msg("average strip length < %f so triangulating"
                                     % self.STRIPLENCUTOFF)
                    newbranch = branch.get_interchangeable_tri_shape()
                    self.data.replace_global_node(branch, newbranch)
                    branch = newbranch
                    data = newbranch.data
                elif self.STITCH:
                    self.toaster.msg("stitching strips (using %i stitches)"
                                     % len(data.get_strips()))
                    data.set_strips([pyffi.utils.tristrip.stitchStrips(data.get_strips())])

        # update skin data
        if branch.skin_instance:
            self.toaster.msg("update skin data vertex mapping")
            skindata = branch.skin_instance.data
            newweights = []
            for i in xrange(new_numvertices):
                newweights.append(oldweights[v_map_inverse[i]])
            for bonenum, bonedata in enumerate(skindata.bone_list):
                w = []
                for i, weightlist in enumerate(newweights):
                    for bonenum_i, weight_i in weightlist:
                        if bonenum == bonenum_i:
                            w.append((i, weight_i))
                bonedata.num_vertices = len(w)
                bonedata.vertex_weights.update_size()
                for j, (i, weight_i) in enumerate(w):
                    bonedata.vertex_weights[j].index = i
                    bonedata.vertex_weights[j].weight = weight_i

            # update skin partition (only if branch already exists)
            branch._validateSkin()
            skininst = branch.skin_instance
            skinpart = skininst.skin_partition
            if not skinpart:
                skinpart = skininst.data.skin_partition

            if skinpart:
                self.toaster.msg("updating skin partition")
                # use Oblivion settings
                branch.update_skin_partition(
                    maxbonesperpartition = 18, maxbonespervertex = 4,
                    stripify = True, verbose = 0)

        # update morph data
        for morphctrl in branch.get_controllers():
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
                morphdata.num_vertices = new_numvertices
                for morph in morphdata.morphs:
                     morph.arg = morphdata.num_vertices # manual argument passing
                     morph.vectors.update_size()

        # recalculate tangent space (only if the branch already exists)
        if branch.find(block_name='Tangent space (binormal & tangent vectors)',
                       block_type=NifFormat.NiBinaryExtraData):
            self.toaster.msg("recalculating tangent space")
            branch.update_tangent_space()

        # stop recursion
        return False

# XXX todo
class SpellSplitGeometry(pyffi.spells.nif.NifSpell):
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

        # has_normals, num_uv_sets, etc. of destdata must already match
        # the sourcedata
        try:
            return v_map[sourceindex]
        except KeyError:
            v_map[sourceindex] = destdata.num_vertices
            destdata.num_vertices += 1
            destdata.vertices.update_size()
            destdata.vertices[-1].x = sourcedata.vertices[sourceindex].x
            destdata.vertices[-1].y = sourcedata.vertices[sourceindex].y
            destdata.vertices[-1].z = sourcedata.vertices[sourceindex].z
            if sourcedata.has_normals:
                destdata.normals.update_size()
                destdata.normals[-1].x = sourcedata.normals[sourceindex].x
                destdata.normals[-1].y = sourcedata.normals[sourceindex].y
                destdata.normals[-1].z = sourcedata.normals[sourceindex].z
            if sourcedata.has_vertex_colors:
                destdata.vertex_colors.update_size()
                destdata.vertex_colors[-1].r = sourcedata.vertex_colors[sourceindex].r
                destdata.vertex_colors[-1].g = sourcedata.vertex_colors[sourceindex].g
                destdata.vertex_colors[-1].b = sourcedata.vertex_colors[sourceindex].b
                destdata.vertex_colors[-1].a = sourcedata.vertex_colors[sourceindex].a
            if sourcedata.has_uv:
                for sourceuvset, destuvset in izip(sourcedata.uv_sets, destdata.uv_sets):
                    destuvset.update_size()
                    destuvset[-1].u = sourceuvset[sourceindex].u
                    destuvset[-1].v = sourceuvset[sourceindex].v
            return destdata.num_vertices

    # XXX todo
    @staticmethod
    def addTriangle(sourcetriangle, v_map, sourcedata, destdata):
        """Add a triangle from source to destination."""
        desttriangle = [
            destdata.addVertex(sourceindex)
            for sourceindex in sourcetriangle]
        destdata.num_triangles += 1
        destdata.triangles.update_size()
        destdata.triangles[-1].v_1 = desttriangle[0]
        destdata.triangles[-1].v_2 = desttriangle[0]
        destdata.triangles[-1].v_3 = desttriangle[0]

    # XXX todo
    @staticmethod
    def get_size(vertices, triangle):
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
        triangles = geom.data.get_triangles()
        node = NifFormat.NiNode().deepcopy(
            NifFormat.NiAVObject.deepcopy(geom))
        geomsplit = None
        # while there are still triangles to add...
        while triangles:
            if geomsplit is None:
                # split new geometry
                geomsplit = NifFormat.NiTriShape()
                node.add_child(geomsplit)
                geomsplit.data = NifFormat.NiTriShapeData()
                v_map = {}
                # copy relevant data
                geomsplit.name = "%s:%i" % (geom.name, node.num_children - 1)
                geomsplit.data.has_vertices = geom.data.has_vertices
                geomsplit.data.has_normals = geom.data.has_normals
                geomsplit.data.has_vertex_colors = geom.data.has_vertex_colors
                geomsplit.data.num_uv_sets = geom.data.num_uv_sets
                geomsplit.data.has_uv = geom.data.has_uv
                geomsplit.data.uv_sets.update_size()
                # assign it a random triangle
                triangle = triangles.pop(0)
                addTriangle(triangle, v_map, geom.data, geomsplit.data)
            # find face that is close to current geometry
            for triangle in triangles:
                 if get_size(geomsplit.data,
                            tuple(geom.data.vertices[index]
                                  for index in triangle)) < threshold_radius:
                     addTriangle(triangle, v_map, geom.data, geomsplit.data)
                     break
            else:
                # if exceeded, start new geometry
                # first finish some things in geomsplit data
                geomsplit.data.update_center_radius()
                # setting geomsplit to None flags this for
                # the next iteration
                geomsplit = None
        # return grouping node
        return node

    def __init__(self, *args, **kwargs):
        pyffi.spells.nif.NifSpell.__init__(self, *args, **kwargs)
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
        # replace block with newblock everywhere
        data.replace_global_node(block, newblock)

        self.optimized.append(block)

        # stop recursing
        return False

class SpellOptimize(
    pyffi.spells.SpellGroupSeries(
        pyffi.spells.SpellGroupParallel(
            pyffi.spells.nif.fix.SpellDelUnusedRoots,
            SpellCleanRefLists,
            pyffi.spells.nif.fix.SpellDetachHavokTriStripsData,
            pyffi.spells.nif.fix.SpellFixTexturePath,
            pyffi.spells.nif.fix.SpellClampMaterialAlpha),
        SpellMergeDuplicates,
        SpellOptimizeGeometry)):
    """Global fixer and optimizer spell."""
    SPELLNAME = "optimize"

class SpellDelUnusedBones(pyffi.spells.nif.NifSpell):
    """Remove empty and duplicate entries in reference lists."""

    SPELLNAME = "opt_delunusedbones"
    READONLY = False

    def datainspect(self):
        # only run the spell if there are skinned geometries
        return self.inspectblocktype(NifFormat.NiSkinInstance)

    def dataentry(self):
        # make list of used bones
        self._used_bones = set()
        for branch in self.data.get_global_iterator():
            if isinstance(branch, NifFormat.NiGeometry):
                if branch.skin_instance:
                    self._used_bones |= set(branch.skin_instance.bones)
        return True

    def branchinspect(self, branch):
        # only inspect the NiNode branch
        return isinstance(branch, NifFormat.NiNode)
    
    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiNode):
            if not branch.children and branch not in self._used_bones:
                self.toaster.msg("removing unreferenced bone")
                self.data.replace_global_node(branch, None)
                self.changed = True
                # no need to recurse further
                return False
        return True
