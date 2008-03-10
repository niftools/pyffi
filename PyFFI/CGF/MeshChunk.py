"""Custom MeshChunk functions."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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
#    * Neither the name of the Python File Format Interface
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

def applyScale(self, scale):
    """Apply scale factor on data."""
    if abs(scale - 1.0) < self.cls.EPSILON:
        return
    for vert in self.vertices:
        vert.p.x *= scale
        vert.p.y *= scale
        vert.p.z *= scale

def getVertices(self):
    """Generator for all vertices."""
    if self.vertices:
        for vert in self.vertices:
            yield vert.p
    elif self.verticesData:
        for vert in self.verticesData.vertices:
            yield vert

def getNormals(self):
    """Generator for all normals."""
    if self.vertices:
        for vert in self.vertices:
            yield vert.n
    elif self.normalsData:
        for norm in self.normalsData.normals:
            yield norm

def getNumTriangles(self):
    """Get number of triangles."""
    if self.faces:
        return self.numFaces
    elif self.indicesData:
        return self.indicesData.numElements // 3
    else:
        return 0

def getTriangles(self):
    """Generator for all triangles."""
    if self.faces:
        for face in self.faces:
            yield face.v0, face.v1, face.v2
    elif self.indicesData:
        it = iter(self.indicesData.indices)
        while True:
           yield it.next(), it.next(), it.next()

def getUVs(self):
    """Generator for all uv coordinates."""
    if self.uvs:
        for uv in self.uvs:
            yield uv.u, uv.v
    elif self.uvData:
        for uv in self.uvData.uvs:
            yield uv.u, 1.0 - uv.v # OpenGL fix!

def getUVTriangles(self):
    """Generator for all uv triangles."""
    if self.uvFaces:
        for uvface in self.uvFaces:
            yield uvface.t0, uvface.t1, uvface.t2
    elif self.indicesData:
        # Crysis: UV triangles coincide with triangles
        it = iter(self.indicesData.indices)
        while True:
           yield it.next(), it.next(), it.next()

def setVerticesNormals(self, vertices, normals):
    """Set vertices and normals. This should be the first function you call
    when setting mesh geometry data.

    Returns list of chunks that have been added."""
    # Far Cry
    self.numVertices = len(vertices)
    self.vertices.updateSize()

    # Crysis
    self.verticesData = self.cls.DataStreamChunk()
    self.verticesData.dataStreamType = self.cls.DataStreamType.VERTICES
    self.verticesData.bytesPerElement = 12
    self.verticesData.numElements = len(vertices)
    self.verticesData.vertices.updateSize()

    self.normalsData = self.cls.DataStreamChunk()
    self.normalsData.dataStreamType = self.cls.DataStreamType.NORMALS
    self.normalsData.bytesPerElement = 12
    self.normalsData.numElements = len(vertices)
    self.normalsData.normals.updateSize()

    # set vertex coordinates and normals for Far Cry
    for cryvert, vert, norm in izip(self.vertices, vertices, normals):
        cryvert.p.x = vert[0]
        cryvert.p.y = vert[1]
        cryvert.p.z = vert[2]
        cryvert.n.x = norm[0]
        cryvert.n.y = norm[1]
        cryvert.n.z = norm[2]

    # set vertex coordinates and normals for Crysis
    for cryvert, crynorm, vert, norm in izip(self.verticesData.vertices,
                                             self.normalsData.normals,
                                             vertices, normals):
        cryvert.x = vert[0]
        cryvert.y = vert[1]
        cryvert.z = vert[2]
        crynorm.x = norm[0]
        crynorm.y = norm[1]
        crynorm.z = norm[2]
