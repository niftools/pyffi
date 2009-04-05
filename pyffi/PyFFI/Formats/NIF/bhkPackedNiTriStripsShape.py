"""Custom functions for bhkPackedNiTriStripsShape."""

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

from PyFFI.Utils import Inertia

def getMassCenterInertia(self, density = 1, solid = True):
    """Return mass, center, and inertia tensor."""
    return Inertia.getMassCenterInertiaPolyhedron(
        [ vert.asTuple() for vert in self.data.vertices ],
        [ ( hktriangle.triangle.v1,
            hktriangle.triangle.v2,
            hktriangle.triangle.v3 )
          for hktriangle in self.data.triangles ],
        density = density, solid = solid)

def addShape(self, triangles, normals, vertices, layer = 0, material = 0):
    """Pack the given geometry."""
    # add the shape data
    if not self.data:
        self.data = self.cls.hkPackedNiTriStripsData()
    data = self.data
    # increase number of shapes
    num_shapes = self.numSubShapes
    self.numSubShapes = num_shapes + 1
    self.subShapes.updateSize()
    data.numSubShapes = num_shapes + 1
    data.subShapes.updateSize()
    # add the shape
    self.subShapes[num_shapes].layer = layer
    self.subShapes[num_shapes].numVertices = len(vertices)
    self.subShapes[num_shapes].material = material
    data.subShapes[num_shapes].layer = layer
    data.subShapes[num_shapes].numVertices = len(vertices)
    data.subShapes[num_shapes].material = material
    firsttriangle = data.numTriangles
    firstvertex = data.numVertices
    data.numTriangles += len(triangles)
    data.triangles.updateSize()
    for tdata, t, n in zip(data.triangles[firsttriangle:], triangles, normals):
        tdata.triangle.v1 = t[0] + firstvertex
        tdata.triangle.v2 = t[1] + firstvertex
        tdata.triangle.v3 = t[2] + firstvertex
        tdata.normal.x = n[0]
        tdata.normal.y = n[1]
        tdata.normal.z = n[2]
    data.numVertices += len(vertices)
    data.vertices.updateSize()
    for vdata, v in zip(data.vertices[firstvertex:], vertices):
        vdata.x = v[0] / 7.0
        vdata.y = v[1] / 7.0
        vdata.z = v[2] / 7.0

