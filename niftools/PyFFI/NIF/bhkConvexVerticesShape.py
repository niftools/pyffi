"""Custom functions for bhkConvexVerticesShape."""

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

from itertools import izip
argmax = lambda array: max(izip(array, xrange(len(array))))[1] # used in qhull

def applyScale(self, scale):
    """Apply scale factor on data."""
    if abs(scale - 1.0) < self.cls._EPSILON: return
    for v in self.vertices:
        v.x *= scale
        v.y *= scale
        v.z *= scale
    for n in self.normals:
        n.w *= scale

def getCenterArea(self):
    """Calculate center of gravity and area."""

    def qhull(vertices, normal):
        """Simple implementation of the quickhull algorithm in 3 dimensions for
        a set of coplanar points. All vertices must satisfy vert * normal = 0.
        Returns a fan of vertices that makes up the surface."""
        # adapted from
        # http://en.literateprograms.org/Quickhull_(Python,_arrays)
        def dome(verts, base):
            a, b = base
            dists = [ normal.crossproduct(b-a) * (vert-a) for vert in verts ]
            outer = [ vert for vert, dist in izip(verts, dists) if dist > 0.001 ]

            if outer:
                pivot = verts[argmax(dists)]
                return dome(outer, [a, pivot]) \
                       + dome(outer, [pivot, b])[1:]
            else:
                return base
  
        if len(vertices) > 2:
            a, b = vertices[:2]
            return dome(vertices, [a, b]) + dome(vertices, [b, a])[1:-1]
        else:
            return vertices

    centerarea = []
    # iterate over all half spaces
    for norm in self.normals:
        # find vertices that lie on this plane
        normverts = []
        for vert in self.vertices:
            if abs(norm.x * vert.x + norm.y * vert.y + norm.z * vert.z
                   + norm.w) < 0.001:
                normverts.append(vert.getVector3())
        assert(len(normverts) >= 3) # debug
        
        # find center and area of each triangle that makes up this set of
        # coplanar vertices; note that this set is already convex, the
        # qhull algorithm is simply used to sort the vertices into a fan
        fan = qhull(normverts, norm.getVector3())
        for i in xrange(2, len(fan)):
            centerarea.append(
                ( (fan[0] + fan[i-1] + fan[i]) / 3,
                  (fan[i-1] - fan[0]).crossproduct(fan[i] - fan[0]).norm() / 2 ))
    # now return the average center and total area
    totalarea = sum(area for center, area in centerarea)
    return ( [ sum(area * center.x for center, area in centerarea)
               / totalarea,
               sum(area * center.y for center, area in centerarea)
               / totalarea,
               sum(area * center.z for center, area in centerarea)
               / totalarea ],
             totalarea )
