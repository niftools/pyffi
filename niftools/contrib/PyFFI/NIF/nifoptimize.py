#!/usr/bin/python

"""A script for optimizing nif files."""

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
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

from PyFFI.NIF import NifFormat
import NifTester
from PyFFI.Utils import TriStrip

def isequalTriGeomData(shape1, shape2):
    """Compare two NiTriShapeData/NiTriStrips blocks, checks if they are
    equal."""
    # check for object identity
    if shape1 is shape2:
        return True

    # check class
    if not isinstance(shape1, shape2.__class__) \
        or not isinstance(shape2, shape1.__class__):
        return False

    # check some trivial things first
    for attribute in (
        "numVertices", "keepFlags", "compressFlags", "hasVertices",
        "numUvSets", "hasNormals", "center", "radius",
        "hasVertexColors", "hasUv", "consistencyFlags"):
        if getattr(shape1, attribute) != getattr(shape2, attribute):
            return False

    # check vertices (this includes uvs, vcols and normals)
    verthashes1 = [ hsh for hsh in vertexHash(shape1) ]
    verthashes2 = [ hsh for hsh in vertexHash(shape2) ]
    for hash1 in verthashes1:
        if not hash1 in verthashes2:
            return False
    for hash2 in verthashes2:
        if not hash2 in verthashes1:
            return False

    # check triangle list
    triangles1 = [ tuple(verthashes1[i] for i in tri)
                   for tri in shape1.getTriangles() ]
    triangles2 = [ tuple(verthashes2[i] for i in tri)
                   for tri in shape2.getTriangles() ]
    for tri1 in triangles1:
        if not tri1 in triangles2:
            return False
    for tri2 in triangles2:
        if not tri2 in triangles1:
            return False

    # looks pretty identical!
    return True

def vertexHash(block, precision = 200):
    """Generator which identifies unique vertices."""
    verts = block.vertices if block.hasVertices else None
    norms = block.normals if block.hasNormals else None
    uvsets = block.uvSets if len(block.uvSets) else None
    vcols = block.vertexColors if block.hasVertexColors else None
    for i in xrange(block.numVertices):
        h = []
        if verts:
            h.extend([ int(x*precision) for x in [verts[i].x, verts[i].y, verts[i].z] ])
        if norms:
            h.extend([ int(x*precision) for x in [norms[i].x, norms[i].y, norms[i].z] ])
        if uvsets:
            for uvset in uvsets:
                h.extend([ int(x*precision) for x in [uvset[i].u, uvset[i].v] ])
        if vcols:
            h.extend([ int(x*precision) for x in [vcols[i].r, vcols[i].g, vcols[i].b, vcols[i].a ] ])
        yield tuple(h)

def triangulateTriStrips(block):
    """Takes a NiTriStrip block and returns an equivalent NiTriShape block."""
    assert(isinstance(block, NifFormat.NiTriStrips))
    # copy the shape (first to NiTriBasedGeom and then to NiTriShape)
    shape = NifFormat.NiTriShape().deepcopy(
        NifFormat.NiTriBasedGeom().deepcopy(block))
    # copy the geometry without strips
    shapedata = NifFormat.NiTriShapeData().deepcopy(
        NifFormat.NiTriBasedGeomData().deepcopy(block.data))
    # update the shape data
    shapedata.setTriangles(block.data.getTriangles())
    # relink the shape data
    shape.data = shapedata
    # and return the result
    return shape

def stripifyTriShape(block):
    """Takes a NiTriShape block and returns an equivalent NiTriStrips block."""
    assert(isinstance(block, NifFormat.NiTriShape))
    # copy the shape (first to NiTriBasedGeom and then to NiTriStrips)
    strips = NifFormat.NiTriStrips().deepcopy(
        NifFormat.NiTriBasedGeom().deepcopy(block))
    # copy the geometry without triangles
    stripsdata = NifFormat.NiTriStripsData().deepcopy(
        NifFormat.NiTriBasedGeomData().deepcopy(block.data))
    # update the shape data
    stripsdata.setTriangles(block.data.getTriangles())
    # relink the shape data
    strips.data = stripsdata
    # and return the result
    return strips

def optimizeTriBasedGeom(block, striplencutoff = 10.0, stitch = True):
    """Optimize a NiTriStrips or NiTriShape block."""
    print "optimizing block '%s'"%block.name

    # cover degenerate case
    if block.data.numVertices < 3:
        print "  less than 3 vertices: removing block"
        return None

    data = block.data

    print "  removing duplicate vertices"
    v_map = [0 for i in xrange(data.numVertices)] # maps old index to new index
    v_map_inverse = [] # inverse: map new index to old index
    k_map = {} # maps hash to new vertex index
    index = 0  # new vertex index for next vertex
    for i, vhash in enumerate(vertexHash(data)):
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
    print "  (num vertices was %i and is now %i)"%(len(v_map), new_numvertices)
    # copy old data
    oldverts = [[v.x, v.y, v.z] for v in data.vertices]
    oldnorms = [[n.x, n.y, n.z] for n in data.normals]
    olduvs   = [[[uv.u, uv.v] for uv in uvset] for uvset in data.uvSets]
    oldvcols = [[c.r, c.g, c.b, c.a] for c in data.vertexColors]
    if block.skinInstance: # for later
        oldweights = block.getVertexWeights()
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
    if isinstance(block, NifFormat.NiTriStrips):
        for strip in data.points:
            for i in xrange(len(strip)):
                strip[i] = v_map[strip[i]]
    elif isinstance(block, NifFormat.NiTriShape):
        for tri in data.triangles:
            tri.v1 = v_map[tri.v1]
            tri.v2 = v_map[tri.v2]
            tri.v3 = v_map[tri.v3]

    # stripify trishape/tristrip
    if isinstance(block, NifFormat.NiTriStrips):
        print "  recalculating strips"
        origlen = sum(i for i in data.stripLengths)
        data.setTriangles(data.getTriangles())
        newlen = sum(i for i in data.stripLengths)
        print "  (strip length was %i and is now %i)" % (origlen, newlen)
    elif isinstance(block, NifFormat.NiTriShape):
        print "  stripifying"
        block = stripifyTriShape(block)
        data = block.data
    # average, weighed towards large strips
    if isinstance(block, NifFormat.NiTriStrips):
        avgstriplen = float(sum(i * i for i in data.stripLengths)) \
            / sum(i for i in data.stripLengths)
        print "  (average strip length is %f)" % avgstriplen
        if avgstriplen < striplencutoff:
            print("  average strip length less than %f so triangulating"
                  % striplencutoff)
            block = triangulateTriStrips(block)
        elif stitch:
            print "  stitching strips"
            data.setStrips([TriStrip.stitchStrips(data.getStrips())])

    # update skin data
    if block.skinInstance:
        print "  update skin data vertex mapping"
        skindata = block.skinInstance.data
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

        # update skin partition (only if block already exists)
        block._validateSkin()
        skininst = block.skinInstance
        skinpart = skininst.skinPartition
        if not skinpart:
            skinpart = skininst.data.skinPartition

        if skinpart:
            print "  updating skin partition"
            # use Oblivion settings
            block.updateSkinPartition(maxbonesperpartition = 18, maxbonespervertex = 4, stripify = True, verbose = 0)

    # recalculate tangent space (only if the block already exists)
    if block.find(block_name = 'Tangent space (binormal & tangent vectors)',
                  block_type = NifFormat.NiBinaryExtraData):
        print "  recalculating tangent space"
        block.updateTangentSpace()

    return block

def fixTexturePath(block, **args):
    if ('\n' in block.fileName) or ('\r' in block.fileName):
        block.fileName = block.fileName.replace('\n', '\\n')
        block.fileName = block.fileName.replace('\r', '\\r')
        print("fixing corrupted file name")
        print("  %s" % block.fileName)

def testRoot(root, **args):
    # check which blocks to exclude
    exclude = args.get("exclude", [])

    # initialize hash maps
    # (each of these dictionaries maps a block hash to an actual block of
    # the given type)
    sourceTextures = {}
    materialProps = {}
    texturingProps = {}
    alphaProps = {}
    specularProps = {}

    # get list of all blocks
    block_list = [ block for block in root.tree(unique = True) ]

    # fix source texture path
    for block in block_list:
        if isinstance(block, NifFormat.NiSourceTexture) \
            and not "NiSourceTexture" in exclude:
            fixTexturePath(block)

    # clamp corrupted material alpha values
    if not "NiMaterialProperty" in exclude:
        for block in block_list:
            # skip non-material blocks
            if not isinstance(block, NifFormat.NiMaterialProperty):
                continue
            # check if alpha exceeds usual values
            if block.alpha > 1:
                # too large
                print("clamping alpha value (%f -> 1.0) in material %s"
                      % (block.alpha, block.name))
                block.alpha = 1.0
            elif block.alpha < 0:
                # too small
                print("clamping alpha value (%f -> 0.0) in material %s"
                      % (block.alpha, block.name))
                block.alpha = 0.0

    # join duplicate source textures
    print("checking for duplicate source textures")
    if not "NiSourceTexture" in exclude:
        for block in block_list:
            # source texture blocks are children of texturing property blocks
            if not isinstance(block, NifFormat.NiTexturingProperty):
                continue
            # check all textures
            for tex in ("Base", "Dark", "Detail", "Gloss", "Glow"):
                if getattr(block, "has%sTexture"%tex):
                    texdesc = getattr(block, "%sTexture"%tex.lower())
                    hashvalue = texdesc.source.getHash()
                    # try to find a matching source texture
                    try:
                        new_texdesc_source = sourceTextures[hashvalue]
                    # if not, save for future reference
                    except KeyError:
                        sourceTextures[hashvalue] = texdesc.source
                    else:
                        # found a match, so report and reassign
                        if texdesc.source != new_texdesc_source:
                            print("  removing duplicate NiSourceTexture block")
                            texdesc.source = new_texdesc_source
                        
    # joining duplicate properties
    print("checking for duplicate properties")
    for block in block_list:
        # check block type
        if not isinstance(block, NifFormat.NiAVObject):
            continue
        
        # remove duplicate and empty properties within the list
        proplist = []
        # construct list of unique and non-empty properties
        for prop in block.properties:
            if not(prop is None or prop in proplist):
                proplist.append(prop)
        # update block properties with the list just constructed
        block.numProperties = len(proplist)
        block.properties.updateSize()
        for i, prop in enumerate(proplist):
            block.properties[i] = prop

        # merge properties
        for i, prop in enumerate(block.properties):
            hashvalue = prop.getHash(ignore_strings = True)
            # join duplicate texturing properties
            if isinstance(prop, NifFormat.NiTexturingProperty) \
                and not "NiTexturingProperty" in exclude:
                try:
                    new_prop = texturingProps[hashvalue]
                except KeyError:
                    texturingProps[hashvalue] = prop
                else:
                    if new_prop != prop:
                        print("  removing duplicate NiTexturingProperty block")
                        block.properties[i] = new_prop
            # join duplicate material properties
            elif isinstance(prop, NifFormat.NiMaterialProperty)\
                and not "NiMaterialProperty" in exclude:
                try:
                    new_prop = materialProps[hashvalue]
                except KeyError:
                    materialProps[hashvalue] = prop
                else:
                    if new_prop != prop:
                        print("  removing duplicate NiMaterialProperty block")
                        block.properties[i] = new_prop
            # join duplicate alpha properties
            elif isinstance(prop, NifFormat.NiAlphaProperty) \
                and not "NiAlphaProperty" in exclude:
                try:
                    new_prop = alphaProps[hashvalue]
                except KeyError:
                    alphaProps[hashvalue] = prop
                else:
                    if new_prop != prop:
                        print("  removing duplicate NiAlphaProperty block")
                        block.properties[i] = new_prop
            # join duplicate specular properties
            elif isinstance(prop, NifFormat.NiSpecularProperty) \
                and not "NiSpecularProperty" in exclude:
                try:
                    new_prop = specularProps[hashvalue]
                except KeyError:
                    specularProps[hashvalue] = prop
                else:
                    if new_prop != prop:
                        print("  removing duplicate NiSpecularProperty block")
                        block.properties[i] = new_prop

    print("optimizing geometries")
    for block in block_list:
        # check if it is a NiNode
        if not isinstance(block, NifFormat.NiNode):
            continue
        
        # remove duplicate and empty children
        childlist = []
        for child in block.children:
            if not(child is None or child in childlist):
                childlist.append(child)
        block.numChildren = len(childlist)
        block.children.updateSize()
        for i, child in enumerate(childlist):
            block.children[i] = child

        # optimize geometries
        for i, child in enumerate(block.children):
           if (isinstance(child, NifFormat.NiTriStrips) \
               and not "NiTriStrips" in exclude) or \
               (isinstance(child, NifFormat.NiTriShape) \
               and not "NiTriShape" in exclude):
               block.children[i] = optimizeTriBasedGeom(child)


    # merge shape data
    # first update list of all blocks
    block_list = [ block for block in root.tree(unique = True) ]
    # then set up list of unique shape data blocks
    # (actually the NiTriShape/NiTriStrips blocks are stored in the list
    # so we can refer back to their name)
    triShapeDataList = []
    for block in block_list:
        if isinstance(block, (NifFormat.NiTriShape, NifFormat.NiTriStrips)):
            # check with all shapes that were already exported
            for shape in triShapeDataList:
                if isequalTriGeomData(shape.data, block.data):
                    # match! so merge
                    block.data = shape.data
                    print("  merging shape data of shape %s with shape %s"
                          % (block.name, shape.name))
                    break
            else:
                # no match, so store for future matching
                triShapeDataList.append(block)

import sys, os
from optparse import OptionParser

def main():
    # parse options and positional arguments
    usage = "%prog [options] <file>|<folder>"
    description="""Optimize nif file <file> or all nif files in folder <folder>.
This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup before running this script."""
    parser = OptionParser(usage, version="%prog $Rev$", description=description)
    parser.add_option("-r", "--raise", dest="raisetesterror",
                      action="store_true",
                      help="raise exception on errors during optimization")
    parser.add_option("-v", "--verbose", dest="verbose",
                      type="int",
                      metavar="VERBOSE",
                      help="verbosity level: 0, 1, or 2 [default: %default]")
    parser.add_option("-p", "--pause", dest="pause",
                      action="store_true",
                      help="pause when done")
    parser.add_option("-x", "--exclude", dest="exclude",
                      action="append",
                      help="exclude given block type from optimization \
(you can exclude multiple block types by specifying this option multiple \
times)")
    parser.set_defaults(raisetesterror = False, verbose = 1, pause = False,
                        exclude = [])
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments (one required)")

    # get top folder/file
    top = args[0]

    # warning
    print("""This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup of your nif files before running this script.
""")
    if not raw_input("Are you sure that you want to proceed? [n/y] ") in ["y", "Y"]:
        if options.pause:
            raw_input("Script aborted by user.")
        else:
            print("Script aborted by user.")
        return

    # run tester
    NifTester.testPath(
        top,
        testRoot = testRoot,
        testFile = NifTester.testFileOverwrite,
        raisereaderror = True, mode = "r+b",
        raisetesterror = options.raisetesterror, verbose = options.verbose,
        exclude = options.exclude)

    if options.pause:
        raw_input("Finished.")

# if script is called...
if __name__ == "__main__":
    main()
