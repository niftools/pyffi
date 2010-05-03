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
from pyffi.utils import unique_map
import pyffi.utils.tristrip
import pyffi.spells
import pyffi.spells.nif
import pyffi.spells.nif.fix

# localization
#import gettext
#_ = gettext.translation('pyffi').ugettext
_ = lambda msg: msg # stub, for now

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
    VERTEXPRECISION = 3
    NORMALPRECISION = 3
    UVPRECISION = 5
    VCOLPRECISION = 3

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

    def optimize_vertices(self, data):
        self.toaster.msg("removing duplicate vertices")
        return unique_map(data.get_vertex_hash_generator(
            vertexprecision=self.VERTEXPRECISION,
            normalprecision=self.NORMALPRECISION,
            uvprecision=self.UVPRECISION,
            vcolprecision=self.VCOLPRECISION))
        
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

        v_map, v_map_inverse = self.optimize_vertices(data)
        
        new_numvertices = len(v_map_inverse)
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
        if (branch.find(block_name='Tangent space (binormal & tangent vectors)',
                        block_type=NifFormat.NiBinaryExtraData)
            or (data.num_uv_sets & 61440)
            or (data.bs_num_uv_sets & 61440)):
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

class SpellReduceGeometry(SpellOptimizeGeometry):
    """Reduce vertices of all geometries:
      - remove duplicate & reduce other vertices
      - stripify if strips are long enough
      - recalculate skin partition
      - recalculate tangent space 
    """

    SPELLNAME = "opt_reducegeometry"
    READONLY = False
    
    @classmethod
    def toastentry(cls, toaster):
        if not toaster.options["arg"]:
            toaster.logger.warn(
                "must specify degree of reduction as argument "
                "(e.g. 2 to reduce a little, 1 to reduce more, "
                "0 to reduce even more, -0.1 is usually the highest "
                "level of optimization possible before significant "
                " graphical oddities occur) to to apply spell")
            return False
        else:
            precision = float(toaster.options["arg"])
            cls.VERTEXPRECISION = precision
            cls.NORMALPRECISION = max(precision, 0)
            cls.UVPRECISION = max(precision, 0)
            cls.VCOLPRECISION = max(precision, 0)
            return True

class SpellPackCollision(pyffi.spells.nif.NifSpell):
    """Pack bhkNiTriStripsShape into bhkPackedNiTriStripsShape."""

    SPELLNAME = "opt_packcollision"
    READONLY = False

    def datainspect(self):
        # only run the spell if there are collision geometries.
        return self.inspectblocktype(NifFormat.bhkNiTriStripsShape)

    def branchinspect(self, branch):
        # only inspect the NiNode branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.bhkCollisionObject,
                                   NifFormat.bhkRigidBody,
                                   NifFormat.bhkMoppBvTreeShape,
                                   NifFormat.bhkNiTriStripsShape))
    
    def branchentry(self, branch):
        if isinstance(branch, NifFormat.bhkNiTriStripsShape):
            new_branch = branch.get_interchangeable_packed_shape()
            self.data.replace_global_node(branch, new_branch)
            self.toaster.msg("collision packed")
            self.changed = True
            # don't need to recurse further
            return False
        # otherwise recurse further
        return True
        
class SpellOptimizeCollisionGeometry(pyffi.spells.nif.NifSpell):
    """Optimize collision geometries by removing duplicate vertices."""

    SPELLNAME = "opt_collisiongeometry"
    READONLY = False
    VERTEXPRECISION = 3

    def __init__(self, *args, **kwargs):
        pyffi.spells.nif.NifSpell.__init__(self, *args, **kwargs)
        # list of all optimized geometries so far
        # (to avoid optimizing the same geometry twice)
        self.optimized = []
        
    def datainspect(self):
        # only run the spell if there are skinned geometries
        return self.inspectblocktype(NifFormat.bhkRigidBody)

    def branchinspect(self, branch):
        # only inspect the NiNode branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.bhkCollisionObject,
                                   NifFormat.bhkRigidBody,
                                   NifFormat.bhkMoppBvTreeShape,
                                   NifFormat.bhkPackedNiTriStripsShape,
                                   NifFormat.bhkNiTriStripsShape,
                                   NifFormat.hkPackedNiTriStripsData,
                                   NifFormat.NiTriStripsData))
        
    def optimize_mopp(self, mopp):
        """Optimize a bhkMoppBvTreeShape."""
        shape = mopp.shape
        data = shape.data

        self.toaster.msg(_("removing duplicate vertices"))
        v_map, v_map_inverse = unique_map(
            data.get_vertex_hash_generator(self.VERTEXPRECISION))
        
        new_numvertices = len(v_map_inverse)
        self.toaster.msg(_("(num vertices in collision shape was %i and is now %i)")
                         % (len(v_map), new_numvertices))
        # copy old data
        oldverts = [[v.x, v.y, v.z] for v in data.vertices]
        # set new data
        data.num_vertices = new_numvertices
        data.vertices.update_size()
        for i, v in enumerate(data.vertices):
            old_i = v_map_inverse[i]
            v.x = oldverts[old_i][0]
            v.y = oldverts[old_i][1]
            v.z = oldverts[old_i][2]
        del oldverts

        # update vertex indices in triangles
        new_triangleindice = []
        i = 0
        for tri in data.triangles:
            tridetail = tri.triangle
            tridetail.v_1 = v_map[tridetail.v_1]
            tridetail.v_2 = v_map[tridetail.v_2]
            tridetail.v_3 = v_map[tridetail.v_3]
            if tridetail.v_1 == tridetail.v_2 or tridetail.v_2 == tridetail.v_3 or tridetail.v_1 == tridetail.v_3:
                continue
            new_triangleindice.append(i)
            new_triangleindice[i] = tri
            i += 1
        # update num triangles and triangles if needed.    
        if data.num_triangles != len(new_triangleindice):
            self.toaster.msg(_("(num triangles in collision shape was %i and is now %i)")
                            % (data.num_triangles, len(new_triangleindice)))
            data.num_triangles = len(new_triangleindice)
            data.triangles.update_size()
            for i, tri in enumerate(data.triangles):
                tri = new_triangleindice[i]
            del new_triangleindice
        if shape.num_sub_shapes == 1:
            shape.sub_shapes[0].num_vertices = shape.data.num_vertices
        #hmm not sure how to do this for multisubshape collisions
        #(determing what subshapes had vertices removed that is
        #not the setting of num vertices for each of them)... ????
        mopp.update_mopp_welding()
        
    def branchentry(self, branch):
        """Optimize a vertex based collision block:
          - remove duplicate vertices
          - rebuild triangle indice and welding info
          - update MOPP data if applicable.
        """
        if branch in self.optimized:
            # already optimized
            return False
        
        # TODO: other collision geometry types
        if (isinstance(branch, NifFormat.bhkMoppBvTreeShape)
            and isinstance(branch.shape, NifFormat.bhkPackedNiTriStripsShape)
            and isinstance(branch.shape.data,
                           NifFormat.hkPackedNiTriStripsData)):
            if branch.shape.data.num_vertices < 3:
                self.toaster.msg(_("less than 3 vertices: removing branch"))
                self.data.replace_global_node(branch, None)
                self.changed = True
                return False                
            self.optimize_mopp(branch)
            # we found a geometry to optimize
            self.optimized.append(branch)
            # we're going to change the data
            self.changed = True
            return False # don't recurese farther
        elif isinstance(branch, NifFormat.bhkNiTriStripsShape):
            # we found a geometry to optimize
            self.optimized.append(branch)
            # we're going to change the data
            self.changed = True
            
            for strips_data in branch.strips_data:
                self.optimized.append(strips_data)

                # cover degenerate case
                if strips_data.num_vertices < 3:
                    self.toaster.msg(_("less than 3 vertices: removing branch"))
                    self.data.replace_global_node(strips_data, None)
                    return False

                # precision of -10 = ignore
                v_map, v_map_inverse = unique_map(
                    strips_data.get_vertex_hash_generator(
                        vertexprecision=self.VERTEXPRECISION,
                        normalprecision=-10,
                        uvprecision=-10,
                        vcolprecision=-10))
                
                new_numvertices = len(v_map_inverse)
                self.toaster.msg(_("(num vertices was %i and is now %i)")
                                 % (len(v_map), new_numvertices))
                # copy old data
                oldverts = [[v.x, v.y, v.z] for v in strips_data.vertices]
                oldnorms = [[n.x, n.y, n.z] for n in strips_data.normals]
                olduvs   = [[[uv.u, uv.v] for uv in uvset] for uvset in strips_data.uv_sets]
                oldvcols = [[c.r, c.g, c.b, c.a] for c in strips_data.vertex_colors]
                # set new data
                strips_data.num_vertices = new_numvertices
                if strips_data.has_vertices:
                    strips_data.vertices.update_size()
                    for i, v in enumerate(strips_data.vertices):
                        old_i = v_map_inverse[i]
                        v.x = oldverts[old_i][0]
                        v.y = oldverts[old_i][1]
                        v.z = oldverts[old_i][2]
                if strips_data.has_normals:
                    strips_data.normals.update_size()
                    for i, n in enumerate(strips_data.normals):
                        old_i = v_map_inverse[i]
                        n.x = oldnorms[old_i][0]
                        n.y = oldnorms[old_i][1]
                        n.z = oldnorms[old_i][2]
                # XXX todo: if ...has_uv_sets...:
                strips_data.uv_sets.update_size()
                for j, uvset in enumerate(strips_data.uv_sets):
                    for i, uv in enumerate(uvset):
                        old_i = v_map_inverse[i]
                        uv.u = olduvs[j][old_i][0]
                        uv.v = olduvs[j][old_i][1]
                if strips_data.has_vertex_colors:
                    strips_data.vertex_colors.update_size()
                    for i, c in enumerate(strips_data.vertex_colors):
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
                for strip in strips_data.points:
                    for i in xrange(len(strip)):
                        try:
                            strip[i] = v_map[strip[i]]
                        except IndexError:
                            self.toaster.logger.warn(
                                _("Corrupt nif: bad vertex index in strip (%i); %s%s") 
                                % (strip[i],
                                _("replacing by valid index which might "),
                                _("modify your geometry!")))
                            if i > 0:
                                strip[i] = strip[i-1]
                            else:
                                strip[i] = strip[i+1]
                        #self.toaster.msg(_("recalculating strips"))
                origlen = sum(i for i in strips_data.strip_lengths)
                strips_data.set_triangles(strips_data.get_triangles())
                newlen = sum(i for i in strips_data.strip_lengths)
                self.toaster.msg(_("(strip length was %i and is now %i)")
                                 % (origlen, newlen))
                return False # No need to keep recursing
        #keep recursing
        return True
        
class SpellOptimizeAnimation(pyffi.spells.nif.NifSpell):
    """Optimizes animations by removing duplicate keys"""

    SPELLNAME = "opt_optimizeanimation"
    READONLY = False
    
    @classmethod
    def toastentry(cls, toaster):
        if not toaster.options["arg"]:
            cls.significance_check = 4
        else:
            cls.significance_check = float(toaster.options["arg"])
        return True


    def datainspect(self):
        # returns more than needed but easiest way to ensure it catches all
        # types of animations
        return True

    def branchinspect(self, branch):
        # inspect the NiAVObject branch, and NiControllerSequence
        # branch (for kf files)
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTimeController,
                                   NifFormat.NiInterpolator,
                                   NifFormat.NiControllerManager,
                                   NifFormat.NiControllerSequence,
                                   NifFormat.NiKeyframeData,
                                   NifFormat.NiTextKeyExtraData,
                                   NifFormat.NiFloatData))

    def optimize_keys(self,keys):
        """Helper function to optimize the keys."""
        new_keys = []
        #compare keys
        ## types: 0 = float/int values
        ##        1 = Vector4, Quaternions, QuaternionsWXYZ
        ##        2 = word values (ie NiTextKeyExtraData)
        ##        3 = Vector3 values (ie translations)
        if len(keys) < 3: return keys # no optimization possible?
        precision = 10**self.significance_check
        if isinstance(keys[0].value,(float,int)):
            for i, key in enumerate(keys):
                if i == 0: # since we don't want to delete the first key even if it is  the same as the last key.
                    new_keys.append(key)
                    continue                
                try:
                    if int(precision*keys[i-1].value) != int(precision*key.value):
                        new_keys.append(key)
                        continue
                    if int(precision*keys[i+1].value) != int(precision*key.value):
                        new_keys.append(key)
                except IndexError:
                    new_keys.append(key)
            return new_keys
        elif isinstance(keys[0].value,(str)):
            for i, key in enumerate(keys):
                if i == 0: # since we don't want to delete the first key even if it is  the same as the last key.
                    new_keys.append(key)
                    continue 
                try:
                    if keys[i-1].value != key.value:
                        new_keys.append(key)
                        continue
                    if keys[i+1].value != key.value:
                        new_keys.append(key)
                except IndexError:
                    new_keys.append(key)
            return new_keys
        elif isinstance(keys[0].value,(NifFormat.Vector4,NifFormat.Quaternion,NifFormat.QuaternionXYZW)):
            tempkey = [[int(keys[0].value.w*precision),int(keys[0].value.x*precision),int(keys[0].value.y*precision),int(keys[0].value.z*precision)],[int(keys[1].value.w*precision),int(keys[1].value.x*precision),int(keys[1].value.y*precision),int(keys[1].value.z*precision)],[int(keys[2].value.w*precision),int(keys[2].value.x*precision),int(keys[2].value.y*precision),int(keys[2].value.z*precision)]]
            for i, key in enumerate(keys):
                if i == 0:
                    new_keys.append(key)
                    continue
                tempkey[0] = tempkey[1]
                tempkey[1] = tempkey[2]
                tempkey[2] = []
                try:
                    tempkey[2].append(int(keys[i+1].value.w*precision))
                    tempkey[2].append(int(keys[i+1].value.x*precision))
                    tempkey[2].append(int(keys[i+1].value.y*precision))
                    tempkey[2].append(int(keys[i+1].value.z*precision))
                except IndexError:
                    new_keys.append(key)
                    continue
                if tempkey[1] != tempkey[0]:
                    new_keys.append(key)
                    continue
                if tempkey[1] != tempkey[2]:
                    new_keys.append(key)
            return new_keys
        elif isinstance(keys[0].value,(NifFormat.Vector3)):
            tempkey = [[int(keys[0].value.x*precision),int(keys[0].value.y*precision),int(keys[0].value.z*precision)],[int(keys[1].value.x*precision),int(keys[1].value.y*precision),int(keys[1].value.z*precision)],[int(keys[2].value.x*precision),int(keys[2].value.y*precision),int(keys[2].value.z*precision)]]
            for i, key in enumerate(keys):
                if i == 0:
                    new_keys.append(key)
                    continue
                tempkey[0] = tempkey[1]
                tempkey[1] = tempkey[2]
                tempkey[2] = []
                try:
                    tempkey[2].append(int(keys[i+1].value.x*precision))
                    tempkey[2].append(int(keys[i+1].value.y*precision))
                    tempkey[2].append(int(keys[i+1].value.z*precision))
                except IndexError:
                    new_keys.append(key)
                    continue
                if tempkey[1] != tempkey[0]:
                    new_keys.append(key)
                    continue
                if tempkey[1] != tempkey[2]:
                    new_keys.append(key)
            return new_keys
        else: #something unhandled -- but what?
            
            return keys
            
    def update_animation(self,old_keygroup,new_keys):
        self.toaster.msg(_("Num keys was %i and is now %i") % (len(old_keygroup.keys),len(new_keys)))
        old_keygroup.num_keys = len(new_keys)
        old_keygroup.keys.update_size()
        for old_key, new_key in izip(old_keygroup.keys,new_keys):
            old_key.time = new_key.time
            old_key.value = new_key.value
        self.changed = True
        
    def update_animation_quaternion(self,old_keygroup,new_keys):
        self.toaster.msg(_("Num keys was %i and is now %i") % (len(old_keygroup),len(new_keys)))
        old_keygroup.update_size()
        for old_key, new_key in izip(old_keygroup,new_keys):
            old_key.time = new_key.time
            old_key.value = new_key.value
        self.changed = True

    def branchentry(self, branch):
            
        if isinstance(branch, NifFormat.NiKeyframeData):
            # (this also covers NiTransformData)
            if branch.num_rotation_keys != 0:
                if branch.rotation_type == 4:
                    for rotation in branch.xyz_rotations:
                        new_keys = self.optimize_keys(rotation.keys)
                        if len(new_keys) != rotation.num_keys:
                            self.update_animation(rotation,new_keys)
                else:
                    new_keys = self.optimize_keys(branch.quaternion_keys)
                    if len(new_keys) != branch.num_rotation_keys:
                        branch.num_rotation_keys = len(new_keys)
                        self.update_animation_quaternion(branch.quaternion_keys,new_keys)
            if branch.translations.num_keys != 0:
                new_keys = self.optimize_keys(branch.translations.keys)
                if len(new_keys) != branch.translations.num_keys:
                    self.update_animation(branch.translations,new_keys)
            if branch.scales.num_keys != 0:
                new_keys = self.optimize_keys(branch.scales.keys)
                if len(new_keys) != branch.scales.num_keys:
                    self.update_animation(branch.scales,new_keys)
            # no children of NiKeyframeData so no need to recurse further
            return False
        elif isinstance(branch, NifFormat.NiTextKeyExtraData):
            self.optimize_keys(branch.text_keys)
            # no children of NiTextKeyExtraData so no need to recurse further
            return False
        elif isinstance(branch, NifFormat.NiFloatData):
            #self.optimize_keys(branch.data.keys)
            # no children of NiFloatData so no need to recurse further
            return False
        else:
            # recurse further
            return True 
        
class SpellOptimize(
    pyffi.spells.SpellGroupSeries(
        pyffi.spells.SpellGroupParallel(
            pyffi.spells.nif.fix.SpellDelUnusedRoots,
            SpellCleanRefLists,
            pyffi.spells.nif.fix.SpellDetachHavokTriStripsData,
            pyffi.spells.nif.fix.SpellFixTexturePath,
            pyffi.spells.nif.fix.SpellClampMaterialAlpha),
        SpellMergeDuplicates,
        SpellOptimizeGeometry,
        SpellPackCollision,
        SpellOptimizeCollisionGeometry)):
    """Global fixer and optimizer spell."""
    SPELLNAME = "optimize"
