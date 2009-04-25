"""Custom functions for NiGeometryData.

>>> from PyFFI.Formats.NIF import NifFormat
>>> geomdata = NifFormat.NiGeometryData()
>>> geomdata.numVertices = 3
>>> geomdata.hasVertices = True
>>> geomdata.hasNormals = True
>>> geomdata.hasVertexColors = True
>>> geomdata.numUvSets = 2
>>> geomdata.vertices.updateSize()
>>> geomdata.normals.updateSize()
>>> geomdata.vertexColors.updateSize()
>>> geomdata.uvSets.updateSize()
>>> geomdata.vertices[0].x = 1
>>> geomdata.vertices[0].y = 2
>>> geomdata.vertices[0].z = 3
>>> geomdata.vertices[1].x = 4
>>> geomdata.vertices[1].y = 5
>>> geomdata.vertices[1].z = 6
>>> geomdata.vertices[2].x = 1.200001
>>> geomdata.vertices[2].y = 3.400001
>>> geomdata.vertices[2].z = 5.600001
>>> geomdata.normals[0].x = 0
>>> geomdata.normals[0].y = 0
>>> geomdata.normals[0].z = 1
>>> geomdata.normals[1].x = 0
>>> geomdata.normals[1].y = 1
>>> geomdata.normals[1].z = 0
>>> geomdata.normals[2].x = 1
>>> geomdata.normals[2].y = 0
>>> geomdata.normals[2].z = 0
>>> geomdata.vertexColors[1].r = 0.310001
>>> geomdata.vertexColors[1].g = 0.320001
>>> geomdata.vertexColors[1].b = 0.330001
>>> geomdata.vertexColors[1].a = 0.340001
>>> geomdata.uvSets[0][0].u = 0.990001
>>> geomdata.uvSets[0][0].v = 0.980001
>>> geomdata.uvSets[0][2].u = 0.970001
>>> geomdata.uvSets[0][2].v = 0.960001
>>> geomdata.uvSets[1][0].v = 0.910001
>>> geomdata.uvSets[1][0].v = 0.920001
>>> geomdata.uvSets[1][2].v = 0.930001
>>> geomdata.uvSets[1][2].v = 0.940001
>>> for h in geomdata.getVertexHashGenerator():
...     print(h)
(1000, 2000, 3000, 0, 0, 1000, 99000, 98000, 0, 92000, 0, 0, 0, 0)
(4000, 5000, 6000, 0, 1000, 0, 0, 0, 0, 0, 310, 320, 330, 340)
(1200, 3400, 5600, 1000, 0, 0, 97000, 96000, 0, 94000, 0, 0, 0, 0)
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

def updateCenterRadius(self):
    """Recalculate center and radius of the data."""
    # in case there are no vertices, set center and radius to zero
    if len(self.vertices) == 0:
        self.center.x = 0.0
        self.center.y = 0.0
        self.center.z = 0.0
        self.radius = 0.0
        return

    # find extreme values in x, y, and z direction
    lowx = min([v.x for v in self.vertices])
    lowy = min([v.y for v in self.vertices])
    lowz = min([v.z for v in self.vertices])
    highx = max([v.x for v in self.vertices])
    highy = max([v.y for v in self.vertices])
    highz = max([v.z for v in self.vertices])

    # center is in the center of the bounding box
    cx = (lowx + highx) * 0.5
    cy = (lowy + highy) * 0.5
    cz = (lowz + highz) * 0.5
    self.center.x = cx
    self.center.y = cy
    self.center.z = cz

    # radius is the largest distance from the center
    r2 = 0.0
    for v in self.vertices:
        dx = cx - v.x
        dy = cy - v.y
        dz = cz - v.z
        r2 = max(r2, dx*dx+dy*dy+dz*dz)
    self.radius = r2 ** 0.5

def applyScale(self, scale):
    """Apply scale factor on data."""
    if abs(scale - 1.0) < self.cls._EPSILON: return
    for v in self.vertices:
        v.x *= scale
        v.y *= scale
        v.z *= scale
    self.center.x *= scale
    self.center.y *= scale
    self.center.z *= scale
    self.radius *= scale

def getVertexHashGenerator(self,
                           vertexprecision=3, normalprecision=3,
                           uvprecision=5, vcolprecision=3):
    """Generator which produces a tuple of integers for each
    (vertex, normal, uv, vcol), to ease detection of duplicate vertices.
    The precision parameters denote number of significant digits.

    Default for uvprecision is higher than default for the rest because
    for very large models the uv coordinates can be very close together.

    :param vertexprecision: Precision to be used for vertices.
    :type vertexprecision: float
    :param normalprecision: Precision to be used for normals.
    :type normalprecision: float
    :param uvprecision: Precision to be used for uvs.
    :type uvprecision: float
    :param vcolprecision: Precision to be used for vertex colors.
    :type vcolprecision: float
    :return: A generator yielding a hash value for each vertex.
    """
    verts = self.vertices if self.hasVertices else None
    norms = self.normals if self.hasNormals else None
    uvsets = self.uvSets if len(self.uvSets) else None
    vcols = self.vertexColors if self.hasVertexColors else None
    vertexfactor = 10 ** vertexprecision
    normalfactor = 10 ** normalprecision
    uvfactor = 10 ** uvprecision
    vcolfactor = 10 ** vcolprecision
    for i in xrange(self.numVertices):
        h = []
        if verts:
            h.extend([int(x * vertexfactor)
                     for x in [verts[i].x, verts[i].y, verts[i].z]])
        if norms:
            h.extend([int(x * normalfactor)
                      for x in [norms[i].x, norms[i].y, norms[i].z]])
        if uvsets:
            for uvset in uvsets:
                h.extend([int(x*uvfactor) for x in [uvset[i].u, uvset[i].v]])
        if vcols:
            h.extend([int(x * vcolfactor)
                      for x in [vcols[i].r, vcols[i].g,
                                vcols[i].b, vcols[i].a]])
        yield tuple(h)
