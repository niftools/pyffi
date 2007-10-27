#!/usr/bin/python

"""A script for optimizing nif files."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
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
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

import NifTester

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

def optimizeTriStrips(block):
    print "optimizing block '%s'"%block.name
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

    # update vertex indices in strips
    for strip in data.points:
        for i in xrange(len(strip)):
            strip[i] = v_map[strip[i]]

    # stripify trishape/tristrip
    print "  recalculating strips"
    origlen = sum(i for i in data.stripLengths)
    data.setTriangles(data.getTriangles())
    newlen = sum(i for i in data.stripLengths)
    print "  (strip length was %i and is now %i)"%(origlen, newlen)

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

        print "  updating skin partition"
        block._validateSkin()
        skininst = block.skinInstance
        skinpart = skininst.skinPartition
        if not skinpart:
            skinpart = skininst.data.skinPartition

        # use Oblivion settings
        block.updateSkinPartition(maxbonesperpartition = 18, maxbonespervertex = 4, stripify = True, verbose = 0)

    # recalculate tangent space
    print "  recalculating tangent space"
    block.updateTangentSpace()

def testRoot(root, **args):
    print("checking for duplicate properties")
    # initialize hash maps
    # (each of these dictionaries maps a block hash to an actual block of
    # the given type)
    sourceTextures = {}
    materialProps = {}
    texturingProps = {}
    alphaProps = {}
    specularProps = {}
    # join duplicate source textures
    for block in root.tree(block_type = NifFormat.NiTexturingProperty):
        for tex in ("Base", "Dark", "Detail", "Gloss", "Glow"):
            if getattr(block, "has%sTexture"%tex):
                texdesc = getattr(block, "%sTexture"%tex.lower())
                hashvalue = texdesc.source.getHash()
                try:
                    new_texdesc_source = sourceTextures[hashvalue]
                except KeyError:
                    sourceTextures[hashvalue] = texdesc.source
                else:
                    if texdesc.source != new_texdesc_source:
                        print("  removing duplicate NiSourceTexture block")
                        texdesc.source = new_texdesc_source
    for block in root.tree(block_type = NifFormat.NiAVObject):
        for i, prop in enumerate(block.properties):
            hashvalue = prop.getHash()
            # join duplicate texturing properties
            if isinstance(prop, NifFormat.NiTexturingProperty):
                try:
                    new_prop = texturingProps[hashvalue]
                except KeyError:
                    texturingProps[hashvalue] = prop
                else:
                    if new_prop != prop:
                        print("  removing duplicate NiTexturingProperty block")
                        block.properties[i] = new_prop
            # join duplicate material properties
            elif isinstance(prop, NifFormat.NiMaterialProperty):
                try:
                    new_prop = materialProps[hashvalue]
                except KeyError:
                    materialProps[hashvalue] = prop
                else:
                    if new_prop != prop:
                        print("  removing duplicate NiMaterialProperty block")
                        block.properties[i] = new_prop
            # join duplicate alpha properties
            elif isinstance(prop, NifFormat.NiAlphaProperty):
                try:
                    new_prop = alphaProps[hashvalue]
                except KeyError:
                    alphaProps[hashvalue] = prop
                else:
                    if new_prop != prop:
                        print("  removing duplicate NiAlphaProperty block")
                        block.properties[i] = new_prop
            # join duplicate specular properties
            elif isinstance(prop, NifFormat.NiSpecularProperty):
                try:
                    new_prop = specularProps[hashvalue]
                except KeyError:
                    specularProps[hashvalue] = prop
                else:
                    if new_prop != prop:
                        print("  removing duplicate NiSpecularProperty block")
                        block.properties[i] = new_prop

def testBlock(block, **args):
    if isinstance(block, NifFormat.NiTriStrips):
        optimizeTriStrips(block)

import sys, os
from optparse import OptionParser

from PyFFI.NIF import NifFormat

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
    parser.set_defaults(raisetesterror = False, verbose = 1)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments (one required)")

    # get top folder/file
    top = args[0]

    # warning
    print """This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup of your nif files before running this script.
"""
    if raw_input("Are you sure that you want to proceed? [n/Y] ") != "Y":
        return

    # run tester
    NifTester.testPath(
        top,
        testBlock = testBlock, testRoot = testRoot,
        testFile = NifTester.testFileOverwrite,
        onreaderror = NifTester.raise_exception, mode = "r+b",
        raisetesterror = options.raisetesterror, verbose = options.verbose)

# if script is called...
if __name__ == "__main__":
    main()
