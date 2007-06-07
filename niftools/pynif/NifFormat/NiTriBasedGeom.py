# --------------------------------------------------------------------------
# NifFormat.NiTriBasedGeom
# Custom functions for NiTriBasedGeom.
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

import struct

def updateTangentSpace(self):
    """Recalculate tangent space data."""
    # check that self.data exists and is valid
    if not isinstance(self.data, self.cls.NiTriBasedGeomData):
        raise ValueError('cannot update tangent space of a geometry with %s data'%(self.data.__class__ if self.data else 'no'))
    
    verts = self.data.vertices
    norms = self.data.normals
    uvs   = self.data.uvSets[0]
    
    # TODO check that verts norms and uvs are ok
    
    tan = [None] * self.data.numVertices
    bin = [None] * self.data.numVertices

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
        r = (1 if r >= 0 else -1)

        # contribution of this triangle to tangents and binormals
        sdir = self.cls.Vector3()
        sdir.x = w3w1.v * v2v1.x - w2w1.v * v3v1.x
        sdir.y = w3w1.v * v2v1.y - w2w1.v * v3v1.y
        sdir.z = w3w1.v * v2v1.z - w2w1.v * v3v1.z

        tdir = self.cls.Vector3()
        tdir.x = w2w1.u * v2v1.x - w3w1.u * v3v1.x
        tdir.y = w2w1.u * v2v1.y - w3w1.u * v3v1.y
        tdir.z = w2w1.u * v2v1.z - w3w1.u * v3v1.z

        sdir *= r
        tdir *= r

        sdir.normalize()
        tdir.normalize()

        for i in [t1, t2, t3]:
            if tan[i]:
                tan[i] += tdir
            else:
                tan[i] = tdir
            if bin[i]:
                bin[i] += sdir
            else:
                bin[i] = sdir

    for i in xrange(self.data.numVertices):
        n = norms[i]
        if (not tan[i]) or (not bin[i]):
            # get a vector orthogonal to the normal
            tan[i].x = n.y
            tan[i].y = n.z
            tan[i].z = n.x
            # get a vector orthogonal to normal and tangent
            bin[i].x = n.y*n.x - n.z*n.z
            bin[i].y = n.z*n.y - n.x*n.x
            bin[i].z = n.x*n.z - n.y*n.y
        else:
            # get component in the plane orthogonal to the normal
            tan[i].normalize()
            tan[i] -= n * (n * tan[i])
            tan[i].normalize()

            # get component in the plane orthogonal to the tangent
            # TODO should this not be the cross product of tangent and normal?
            bin[i].normalize()
            bin[i] -= tan[i] * (tan[i] * bin[i])
            bin[i].normalize()

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
    block.binaryData.dataSize = self.data.numVertices * 24
    block.binaryData.data.updateSize()
    cnt = 0
    for v in tan + bin:
        bytes = struct.pack('<fff', v.x, v.y, v.z)
        for b in bytes:
            block.binaryData.data[cnt] = ord(b)
            cnt += 1
