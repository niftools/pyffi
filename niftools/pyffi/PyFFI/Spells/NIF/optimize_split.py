"""A spell for splitting geometries in order to limit the maximal radius,
which results in nif files that run much smoother in the engine."""

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

from itertools import izip

from PyFFI.Formats.NIF import NifFormat

# set flag to overwrite files
__readonly__ = False

# example usage
__examples__ = """* Standard usage:

    python niftoaster.py optimize_split /path/to/copy/of/my/nifs
"""

THRESHOLD_RADIUS = 100 # threshold where to split geometry

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

def testRoot(root, **args):
    """Optimize the tree at root. This is the main entry point for the
    optimize script.

    @param root: The root of the tree.
    @type root: L{NifFormat.NiObject}
    """

    # check which blocks to exclude
    exclude = args.get("exclude", [])

    # get list of all blocks
    block_list = [ block for block in root.tree(unique = True) ]

    # go over all geometries
    optimized_geometries = []
    for block in block_list:
         if isinstance(block, NifFormat.NiGeometry):
             # avoid doing the same block twice
             if block in optimized_geometries:
                 continue
             # get geometry data
             geomdata = block.data
             if not geomdata:
                 optimized_geometries.append(block)
                 continue
             # check radius
             if geomdata.radius < THRESHOLD_RADIUS:
                 optimized_geometries.append(block)
                 continue
             # radius is over the threshold, so re-organize the geometry
             newblock = split(block, threshold_radius = THRESHOLD_RADIUS)
             # TODO replace block with newblock everywhere (write dedicated
             #      function in PyFFI for replacement)
             root = root.replaceLink(block, newblock)

             optimized_geometries.append(block)

    # root may have changed
    return root

