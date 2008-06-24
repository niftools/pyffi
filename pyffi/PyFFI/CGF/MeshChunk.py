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

import itertools
from itertools import izip
from PyFFI.Utils import MathUtils
from PyFFI.Utils import TangentSpace

def applyScale(self, scale):
    """Apply scale factor on data."""
    if abs(scale - 1.0) < self.cls.EPSILON:
        return
    for vert in self.vertices:
        vert.p.x *= scale
        vert.p.y *= scale
        vert.p.z *= scale

    self.minBound.x *= scale
    self.minBound.y *= scale
    self.minBound.z *= scale
    self.maxBound.x *= scale
    self.maxBound.y *= scale
    self.maxBound.z *= scale

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

def getColors(self):
    """Generator for all vertex colors."""
    if self.vertexColors:
        for color in self.vertexColors:
            # Far Cry has no alpha channel
            yield (color.r, color.g, color.b, 255)
    elif self.colorsData:
        if self.colorsData.rgbColors:
            for color in self.colorsData.rgbColors:
                yield (color.r, color.g, color.b, 255)
        elif self.colorsData.rgbaColors:
            for color in self.colorsData.rgbaColors:
                yield (color.r, color.g, color.b, color.a)

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

def getMaterialIndices(self):
    """Generator for all materials (per triangle)."""
    if self.faces:
        for face in self.faces:
            yield face.material
    elif self.meshSubsets:
        for meshsubset in self.meshSubsets.meshSubsets:
            for i in xrange(meshsubset.numIndices // 3):
                yield meshsubset.matId

def getUVs(self):
    """Generator for all uv coordinates."""
    if self.uvs:
        for uv in self.uvs:
            yield uv.u, uv.v
    elif self.uvsData:
        for uv in self.uvsData.uvs:
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

### DEPRECATED: USE setGeometry INSTEAD ###
def setVerticesNormals(self, vertices, normals):
    """B{Deprecated. Use L{setGeometry} instead.} Set vertices and normals. This used to be the first function to call
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

### STILL WIP!!! ###
def setGeometry(self,
                verticeslist = None, normalslist = None,
                triangleslist = None, matlist = None,
                uvslist = None, colorslist = None):
    """Set geometry data.

    >>> from PyFFI.CGF import CgfFormat
    >>> chunk = CgfFormat.MeshChunk()
    >>> vertices1 = [(0,0,0),(0,1,0),(1,0,0),(1,1,0)]
    >>> vertices2 = [(0,0,1),(0,1,1),(1,0,1),(1,1,1)]
    >>> normals1 = [(0,0,-1),(0,0,-1),(0,0,-1),(0,0,-1)]
    >>> normals2 = [(0,0,1),(0,0,1),(0,0,1),(0,0,1)]
    >>> triangles1 = [(0,1,2),(2,1,3)]
    >>> triangles2 = [(0,1,2),(2,1,3)]
    >>> uvs1 = [(0,0),(0,1),(1,0),(1,1)]
    >>> uvs2 = [(0,0),(0,1),(1,0),(1,1)]
    >>> colors1 = [(0,1,2,3),(4,5,6,7),(8,9,10,11),(12,13,14,15)]
    >>> colors2 = [(50,51,52,53),(54,55,56,57),(58,59,60,61),(62,63,64,65)]
    >>> chunk.setGeometry(verticeslist = [vertices1, vertices2],
    ...                   normalslist = [normals1, normals2],
    ...                   triangleslist = [triangles1, triangles2],
    ...                   uvslist = [uvs1, uvs2],
    ...                   matlist = [2,5],
    ...                   colorslist = [colors1, colors2])
    >>> print chunk # doctest: +ELLIPSIS
    <class 'PyFFI.XmlHandler.MeshChunk'> instance at ...
    * hasVertexWeights : False
    * hasVertexColors : True
    * inWorldSpace : False
    * reserved1 : 0
    * reserved2 : 0
    * flags1 : 0
    * flags2 : 0
    * numVertices : 8
    * numIndices : 12
    * numUvs : 8
    * numFaces : 4
    * material : None
    * numMeshSubsets : 2
    * meshSubsets : <class 'PyFFI.XmlHandler.MeshSubsetsChunk'> instance at ...
    * vertAnim : None
    * vertices :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: <class 'PyFFI.XmlHandler.Vertex'> instance at ...
        * p : [  0.000  0.000  0.000 ]
        * n : [  0.000  0.000 -1.000 ]
        1: <class 'PyFFI.XmlHandler.Vertex'> instance at ...
        * p : [  0.000  1.000  0.000 ]
        * n : [  0.000  0.000 -1.000 ]
        2: <class 'PyFFI.XmlHandler.Vertex'> instance at ...
        * p : [  1.000  0.000  0.000 ]
        * n : [  0.000  0.000 -1.000 ]
        3: <class 'PyFFI.XmlHandler.Vertex'> instance at ...
        * p : [  1.000  1.000  0.000 ]
        * n : [  0.000  0.000 -1.000 ]
        4: <class 'PyFFI.XmlHandler.Vertex'> instance at ...
        * p : [  0.000  0.000  1.000 ]
        * n : [  0.000  0.000  1.000 ]
        5: <class 'PyFFI.XmlHandler.Vertex'> instance at ...
        * p : [  0.000  1.000  1.000 ]
        * n : [  0.000  0.000  1.000 ]
        6: <class 'PyFFI.XmlHandler.Vertex'> instance at ...
        * p : [  1.000  0.000  1.000 ]
        * n : [  0.000  0.000  1.000 ]
        7: <class 'PyFFI.XmlHandler.Vertex'> instance at ...
        * p : [  1.000  1.000  1.000 ]
        * n : [  0.000  0.000  1.000 ]
    * faces :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: <class 'PyFFI.XmlHandler.Face'> instance at ...
        * v0 : 0
        * v1 : 1
        * v2 : 2
        * material : 2
        * smGroup : 1
        1: <class 'PyFFI.XmlHandler.Face'> instance at ...
        * v0 : 2
        * v1 : 1
        * v2 : 3
        * material : 2
        * smGroup : 1
        2: <class 'PyFFI.XmlHandler.Face'> instance at ...
        * v0 : 4
        * v1 : 5
        * v2 : 6
        * material : 5
        * smGroup : 1
        3: <class 'PyFFI.XmlHandler.Face'> instance at ...
        * v0 : 6
        * v1 : 5
        * v2 : 7
        * material : 5
        * smGroup : 1
    * uvs :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 0.0
        * v : 0.0
        1: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 0.0
        * v : 1.0
        2: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 1.0
        * v : 0.0
        3: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 1.0
        * v : 1.0
        4: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 0.0
        * v : 0.0
        5: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 0.0
        * v : 1.0
        6: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 1.0
        * v : 0.0
        7: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 1.0
        * v : 1.0
    * uvFaces :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: <class 'PyFFI.XmlHandler.UVFace'> instance at ...
        * t0 : 0
        * t1 : 1
        * t2 : 2
        1: <class 'PyFFI.XmlHandler.UVFace'> instance at ...
        * t0 : 2
        * t1 : 1
        * t2 : 3
        2: <class 'PyFFI.XmlHandler.UVFace'> instance at ...
        * t0 : 4
        * t1 : 5
        * t2 : 6
        3: <class 'PyFFI.XmlHandler.UVFace'> instance at ...
        * t0 : 6
        * t1 : 5
        * t2 : 7
    * vertexColors :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: <class 'PyFFI.XmlHandler.IRGB'> instance at ...
        * r : 0
        * g : 1
        * b : 2
        1: <class 'PyFFI.XmlHandler.IRGB'> instance at ...
        * r : 4
        * g : 5
        * b : 6
        2: <class 'PyFFI.XmlHandler.IRGB'> instance at ...
        * r : 8
        * g : 9
        * b : 10
        3: <class 'PyFFI.XmlHandler.IRGB'> instance at ...
        * r : 12
        * g : 13
        * b : 14
        4: <class 'PyFFI.XmlHandler.IRGB'> instance at ...
        * r : 50
        * g : 51
        * b : 52
        5: <class 'PyFFI.XmlHandler.IRGB'> instance at ...
        * r : 54
        * g : 55
        * b : 56
        6: <class 'PyFFI.XmlHandler.IRGB'> instance at ...
        * r : 58
        * g : 59
        * b : 60
        7: <class 'PyFFI.XmlHandler.IRGB'> instance at ...
        * r : 62
        * g : 63
        * b : 64
    * verticesData : <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * normalsData : <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * uvsData : <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * colorsData : <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * colors2Data : None
    * indicesData : <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * tangentsData : <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * shCoeffsData : None
    * shapeDeformationData : None
    * boneMapData : None
    * faceMapData : None
    * vertMatsData : None
    * reservedData :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: None
        1: None
        2: None
        3: None
    * physicsData :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: None
        1: None
        2: None
        3: None
    * minBound : [  0.000  0.000  0.000 ]
    * maxBound : [  1.000  1.000  1.000 ]
    * reserved3 :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: 0
        1: 0
        2: 0
        3: 0
        4: 0
        5: 0
        6: 0
        7: 0
        8: 0
        9: 0
        10: 0
        11: 0
        12: 0
        13: 0
        14: 0
        15: 0
        16: 0
        etc...
    <BLANKLINE>
    >>> print chunk.meshSubsets # doctest: +ELLIPSIS
    <class 'PyFFI.XmlHandler.MeshSubsetsChunk'> instance at ...
    * flags :
        <class 'PyFFI.XmlHandler.MeshSubsetsFlags'> instance at ...
        * shHasDecomprMat : 0
        * boneIndices : 0
    * numMeshSubsets : 2
    * reserved1 : 0
    * reserved2 : 0
    * meshSubsets :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: <class 'PyFFI.XmlHandler.MeshSubset'> instance at ...
        * firstIndex : 0
        * numIndices : 6
        * firstVertex : 0
        * numVertices : 4
        * matId : 2
        * radius : 0.707106769...
        * center : [  0.500  0.500  0.000 ]
        1: <class 'PyFFI.XmlHandler.MeshSubset'> instance at ...
        * firstIndex : 6
        * numIndices : 6
        * firstVertex : 4
        * numVertices : 4
        * matId : 5
        * radius : 0.707106769...
        * center : [  0.500  0.500  1.000 ]
    <BLANKLINE>
    >>> print chunk.verticesData # doctest: +ELLIPSIS
    <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * flags : 0
    * dataStreamType : VERTICES
    * numElements : 8
    * bytesPerElement : 12
    * reserved1 : 0
    * reserved2 : 0
    * vertices :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: [  0.000  0.000  0.000 ]
        1: [  0.000  1.000  0.000 ]
        2: [  1.000  0.000  0.000 ]
        3: [  1.000  1.000  0.000 ]
        4: [  0.000  0.000  1.000 ]
        5: [  0.000  1.000  1.000 ]
        6: [  1.000  0.000  1.000 ]
        7: [  1.000  1.000  1.000 ]
    <BLANKLINE>
    >>> print chunk.normalsData # doctest: +ELLIPSIS
    <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * flags : 0
    * dataStreamType : NORMALS
    * numElements : 8
    * bytesPerElement : 12
    * reserved1 : 0
    * reserved2 : 0
    * normals :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: [  0.000  0.000 -1.000 ]
        1: [  0.000  0.000 -1.000 ]
        2: [  0.000  0.000 -1.000 ]
        3: [  0.000  0.000 -1.000 ]
        4: [  0.000  0.000  1.000 ]
        5: [  0.000  0.000  1.000 ]
        6: [  0.000  0.000  1.000 ]
        7: [  0.000  0.000  1.000 ]
    <BLANKLINE>
    >>> print chunk.indicesData # doctest: +ELLIPSIS
    <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * flags : 0
    * dataStreamType : INDICES
    * numElements : 12
    * bytesPerElement : 2
    * reserved1 : 0
    * reserved2 : 0
    * indices :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: 0
        1: 1
        2: 2
        3: 2
        4: 1
        5: 3
        6: 4
        7: 5
        8: 6
        9: 6
        10: 5
        11: 7
    <BLANKLINE>
    >>> print chunk.uvsData # doctest: +ELLIPSIS
    <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * flags : 0
    * dataStreamType : UVS
    * numElements : 8
    * bytesPerElement : 8
    * reserved1 : 0
    * reserved2 : 0
    * uvs :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 0.0
        * v : 1.0
        1: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 0.0
        * v : 0.0
        2: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 1.0
        * v : 1.0
        3: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 1.0
        * v : 0.0
        4: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 0.0
        * v : 1.0
        5: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 0.0
        * v : 0.0
        6: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 1.0
        * v : 1.0
        7: <class 'PyFFI.XmlHandler.UV'> instance at ...
        * u : 1.0
        * v : 0.0
    <BLANKLINE>
    >>> print chunk.tangentsData # doctest: +ELLIPSIS
    <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * flags : 0
    * dataStreamType : TANGENTS
    * numElements : 8
    * bytesPerElement : 16
    * reserved1 : 0
    * reserved2 : 0
    * tangents :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0, 0: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 32767
        * y : 0
        * z : 0
        * w : 32767
        0, 1: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 0
        * y : -32767
        * z : 0
        * w : 32767
        1, 0: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 32767
        * y : 0
        * z : 0
        * w : 32767
        1, 1: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 0
        * y : -32767
        * z : 0
        * w : 32767
        2, 0: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 32767
        * y : 0
        * z : 0
        * w : 32767
        2, 1: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 0
        * y : -32767
        * z : 0
        * w : 32767
        3, 0: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 32767
        * y : 0
        * z : 0
        * w : 32767
        3, 1: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 0
        * y : -32767
        * z : 0
        * w : 32767
        4, 0: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 32767
        * y : 0
        * z : 0
        * w : 32767
        4, 1: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 0
        * y : -32767
        * z : 0
        * w : 32767
        5, 0: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 32767
        * y : 0
        * z : 0
        * w : 32767
        5, 1: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 0
        * y : -32767
        * z : 0
        * w : 32767
        6, 0: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 32767
        * y : 0
        * z : 0
        * w : 32767
        6, 1: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 0
        * y : -32767
        * z : 0
        * w : 32767
        7, 0: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 32767
        * y : 0
        * z : 0
        * w : 32767
        7, 1: <class 'PyFFI.XmlHandler.Tangent'> instance at ...
        * x : 0
        * y : -32767
        * z : 0
        * w : 32767
    <BLANKLINE>
    >>> print chunk.colorsData # doctest: +ELLIPSIS
    <class 'PyFFI.XmlHandler.DataStreamChunk'> instance at ...
    * flags : 0
    * dataStreamType : COLORS
    * numElements : 8
    * bytesPerElement : 4
    * reserved1 : 0
    * reserved2 : 0
    * rgbaColors :
        <class 'PyFFI.Bases.Array.Array'> instance at ...
        0: <class 'PyFFI.XmlHandler.IRGBA'> instance at ...
        * r : 0
        * g : 1
        * b : 2
        * a : 3
        1: <class 'PyFFI.XmlHandler.IRGBA'> instance at ...
        * r : 4
        * g : 5
        * b : 6
        * a : 7
        2: <class 'PyFFI.XmlHandler.IRGBA'> instance at ...
        * r : 8
        * g : 9
        * b : 10
        * a : 11
        3: <class 'PyFFI.XmlHandler.IRGBA'> instance at ...
        * r : 12
        * g : 13
        * b : 14
        * a : 15
        4: <class 'PyFFI.XmlHandler.IRGBA'> instance at ...
        * r : 50
        * g : 51
        * b : 52
        * a : 53
        5: <class 'PyFFI.XmlHandler.IRGBA'> instance at ...
        * r : 54
        * g : 55
        * b : 56
        * a : 57
        6: <class 'PyFFI.XmlHandler.IRGBA'> instance at ...
        * r : 58
        * g : 59
        * b : 60
        * a : 61
        7: <class 'PyFFI.XmlHandler.IRGBA'> instance at ...
        * r : 62
        * g : 63
        * b : 64
        * a : 65
    <BLANKLINE>

    @param verticeslist: A list of lists of vertices (one list per material).
    @param normalslist: A list of lists of normals (one list per material).
    @param triangleslist: A list of lists of triangles (one list per material).
    @param matlist: A list of material indices. Optional.
    @param uvslist: A list of lists of uvs (one list per material). Optional.
    @param colorslist: A list of lists of RGBA colors (one list per material).
        Optional. Each color is a tuple (r, g, b, a) with each component an
        integer between 0 and 255.
    """
    # argument sanity checking
    # check length of lists
    if len(verticeslist) != len(normalslist):
        raise ValueError("normalslist must have same length as verticeslist")
    if len(triangleslist) != len(normalslist):
        raise ValueError("triangleslist must have same length as verticeslist")
    if not matlist is None and len(verticeslist) != len(matlist):
        raise ValueError("matlist must have same length as verticeslist")
    if not uvslist is None and len(verticeslist) != len(uvslist):
        raise ValueError("uvslist must have same length as verticeslist")
    if not colorslist is None and len(verticeslist) != len(colorslist):
        raise ValueError("colorslist must have same length as verticeslist")

    # check length of lists in lists
    for vertices, normals in izip(verticeslist, normalslist):
        if len(vertices) != len(normals):
            raise ValueError("vertex and normal lists must have same length")
    if not uvslist is None:
        for vertices, uvs in izip(verticeslist, uvslist):
            if len(vertices) != len(uvs):
                raise ValueError("vertex and uv lists must have same length")
    if not colorslist is None:
        for vertices, colors in izip(verticeslist, colorslist):
            if len(vertices) != len(colors):
                raise ValueError("vertex and color lists must have same length")

    # get total number of vertices
    numvertices = sum(len(vertices) for vertices in verticeslist)
    if numvertices > 65535:
        raise ValueError("cannot store geometry: too many vertices (%i and maximum is 65535)")
    numtriangles = sum(len(triangles) for triangles in triangleslist)

    # Far Cry data preparation
    self.numVertices = numvertices
    self.vertices.updateSize()
    selfvertices_iter = iter(self.vertices)
    self.numFaces = numtriangles
    self.faces.updateSize()
    selffaces_iter = iter(self.faces)
    if not uvslist is None:
        self.numUvs = numvertices
        self.uvs.updateSize()
        self.uvFaces.updateSize()
        selfuvs_iter = iter(self.uvs)
        selfuvFaces_iter = iter(self.uvFaces)
    if not colorslist is None:
        self.hasVertexColors = True
        self.vertexColors.updateSize()
        selfvertexColors_iter = iter(self.vertexColors)

    # Crysis data preparation
    self.numIndices = numtriangles * 3

    self.verticesData = self.cls.DataStreamChunk()
    self.verticesData.dataStreamType = self.cls.DataStreamType.VERTICES
    self.verticesData.bytesPerElement = 12
    self.verticesData.numElements = numvertices
    self.verticesData.vertices.updateSize()
    selfverticesData_iter = iter(self.verticesData.vertices)

    self.normalsData = self.cls.DataStreamChunk()
    self.normalsData.dataStreamType = self.cls.DataStreamType.NORMALS
    self.normalsData.bytesPerElement = 12
    self.normalsData.numElements = numvertices
    self.normalsData.normals.updateSize()
    selfnormalsData_iter = iter(self.normalsData.normals)

    self.indicesData = self.cls.DataStreamChunk()
    self.indicesData.dataStreamType = self.cls.DataStreamType.INDICES
    self.indicesData.bytesPerElement = 2
    self.indicesData.numElements = numtriangles * 3
    self.indicesData.indices.updateSize()

    if not uvslist is None:
        # uvs
        self.uvsData = self.cls.DataStreamChunk()
        self.uvsData.dataStreamType = self.cls.DataStreamType.UVS
        self.uvsData.bytesPerElement = 8
        self.uvsData.numElements = numvertices
        self.uvsData.uvs.updateSize()
        selfuvsData_iter = iter(self.uvsData.uvs)
        # have tangent space
        has_tangentspace = True
    else:
        # no tangent space
        has_tangentspace = False

    if not colorslist is None:
        # vertex colors
        self.colorsData = self.cls.DataStreamChunk()
        self.colorsData.dataStreamType = self.cls.DataStreamType.COLORS
        self.colorsData.bytesPerElement = 4
        self.colorsData.numElements = numvertices
        self.colorsData.rgbaColors.updateSize()
        selfcolorsData_iter = iter(self.colorsData.rgbaColors)

    self.numMeshSubsets = len(verticeslist)
    self.meshSubsets = self.cls.MeshSubsetsChunk()
    self.meshSubsets.numMeshSubsets = self.numMeshSubsets
    self.meshSubsets.meshSubsets.updateSize()

    # set up default iterators
    if matlist is None:
        matlist = itertools.repeat(0)
    if uvslist is None:
        uvslist = itertools.repeat(None)
    if colorslist is None:
        colorslist = itertools.repeat(None)

    # now iterate over all materials
    firstvertexindex = 0
    firstindicesindex = 0
    for vertices, normals, triangles, mat, uvs, colors, meshsubset in izip(
        verticeslist, normalslist,
        triangleslist, matlist,
        uvslist, colorslist,
        self.meshSubsets.meshSubsets):

        # set Crysis mesh subset info
        meshsubset.firstIndex = firstindicesindex
        meshsubset.numIndices = len(triangles) * 3
        meshsubset.firstVertex = firstvertexindex
        meshsubset.numVertices = len(vertices)
        meshsubset.matId = mat
        center, radius = MathUtils.getCenterRadius(vertices)
        meshsubset.radius = radius
        meshsubset.center.x = center[0]
        meshsubset.center.y = center[1]
        meshsubset.center.z = center[2]

        # set vertex coordinates and normals for Far Cry
        for vert, norm in izip(vertices, normals):
            cryvert = selfvertices_iter.next()
            cryvert.p.x = vert[0]
            cryvert.p.y = vert[1]
            cryvert.p.z = vert[2]
            cryvert.n.x = norm[0]
            cryvert.n.y = norm[1]
            cryvert.n.z = norm[2]

        # set vertex coordinates and normals for Crysis
        for vert, norm in izip(vertices, normals):
            cryvert = selfverticesData_iter.next()
            crynorm = selfnormalsData_iter.next()
            cryvert.x = vert[0]
            cryvert.y = vert[1]
            cryvert.z = vert[2]
            crynorm.x = norm[0]
            crynorm.y = norm[1]
            crynorm.z = norm[2]

        # set Far Cry face info
        for triangle in triangles:
            cryface = selffaces_iter.next()
            cryface.v0 = triangle[0] + firstvertexindex
            cryface.v1 = triangle[1] + firstvertexindex
            cryface.v2 = triangle[2] + firstvertexindex
            cryface.material = mat

        # set Crysis face info
        for i, vertexindex in enumerate(itertools.chain(*triangles)):
            self.indicesData.indices[i + firstindicesindex] \
                = vertexindex + firstvertexindex

        if not uvs is None:
            # set Far Cry uv info
            for triangle in triangles:
                cryuvface = selfuvFaces_iter.next()
                cryuvface.t0 = triangle[0] + firstvertexindex
                cryuvface.t1 = triangle[1] + firstvertexindex
                cryuvface.t2 = triangle[2] + firstvertexindex
            for uv in uvs:
                cryuv = selfuvs_iter.next()
                cryuv.u = uv[0]
                cryuv.v = uv[1]

            # set Crysis uv info
            for uv in uvs:
                cryuv = selfuvsData_iter.next()
                cryuv.u = uv[0]
                cryuv.v = 1.0 - uv[1] # OpenGL fix

        if not colors is None:
            # set Far Cry color info
            for color in colors:
                crycolor = selfvertexColors_iter.next()
                crycolor.r = color[0]
                crycolor.g = color[1]
                crycolor.b = color[2]
                # note: Far Cry does not support alpha color channel

            # set Crysis color info
            for color in colors:
                crycolor = selfcolorsData_iter.next()
                crycolor.r = color[0]
                crycolor.g = color[1]
                crycolor.b = color[2]
                crycolor.a = color[3]

        # update index offsets
        firstvertexindex += len(vertices)
        firstindicesindex += 3 * len(triangles)

    # update tangent space
    if has_tangentspace:
        self.updateTangentSpace()

    # set global bounding box
    minbound, maxbound = MathUtils.getBoundingBox(
        list(itertools.chain(*verticeslist)))
    self.minBound.x = minbound[0]
    self.minBound.y = minbound[1]
    self.minBound.z = minbound[2]
    self.maxBound.x = maxbound[0]
    self.maxBound.y = maxbound[1]
    self.maxBound.z = maxbound[2]

def updateTangentSpace(self):
    """Recalculate tangent space data."""
    # set up tangent space
    self.tangentsData = self.cls.DataStreamChunk()
    self.tangentsData.dataStreamType = self.cls.DataStreamType.TANGENTS
    self.tangentsData.bytesPerElement = 16
    self.tangentsData.numElements = self.numVertices
    self.tangentsData.tangents.updateSize()
    selftangentsData_iter = iter(self.tangentsData.tangents)

    # set Crysis tangents info
    tangents, binormals, orientations = TangentSpace.getTangentSpace(
        vertices = list((vert.x, vert.y, vert.z)
                        for vert in self.verticesData.vertices),
        normals = list((norm.x, norm.y, norm.z)
                        for norm in self.normalsData.normals),
        uvs = list((uv.u, uv.v)
                   for uv in self.uvsData.uvs),
        triangles = list(self.getTriangles()),
        orientation = True)

    for crytangent, tan, bin, orient in izip(self.tangentsData.tangents,
                                             tangents, binormals, orientations):
        if orient > 0:
            tangent_w = 32767
        else:
            tangent_w = -32767
        crytangent[1].x = int(32767 * tan[0])
        crytangent[1].y = int(32767 * tan[1])
        crytangent[1].z = int(32767 * tan[2])
        crytangent[1].w = tangent_w
        crytangent[0].x = int(32767 * bin[0])
        crytangent[0].y = int(32767 * bin[1])
        crytangent[0].z = int(32767 * bin[2])
        crytangent[0].w = tangent_w


if __name__ == "__main__":
    import doctest
    doctest.testmod()
