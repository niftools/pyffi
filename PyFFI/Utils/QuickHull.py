from PyFFI.Utils.MathUtils import *
from itertools import izip
import operator

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, Python File Format Interface
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

_EPSILON = 0.0001

def basesimplex3d(vertices):
    """Find four extreme points, to be used as a starting base for the
    quick hull algorithm. The algorithm tries to find four points that are
    as far apart as possible, because that speeds up the quick hull
    algorithm. The vertices are ordered so their signed volume is positive.

    >>> base = basesimplex3d([(0,0,0),(0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,0,1),(1,1,0),(1,1,1)])
    >>> (0,0,0) in base
    True
    >>> (1,1,1) in base
    True
    """
    # sort axes by their extent in vertices
    extents = sorted(range(3),
                     key=lambda i:
                     max(v[i] for v in vertices)
                     - min(v[i] for v in vertices))
    # extents[0] has the index with largest extent etc.
    # so let us minimize and maximize v with key
    # (v[extents[0]], v[extents[1]], v[extents[2]])
    # which we can write as operator.itemgetter(*extents)(v)
    v0 = min(vertices, key=operator.itemgetter(*extents))
    v1 = max(vertices, key=operator.itemgetter(*extents))
    # as a third extreme point select that one which maximizes the distance
    # from the v0 - v1 axis
    v2 = max(vertices, key=lambda v: vecDistanceAxis((v0, v1), v))
    # as a fourth extreme point select one which maximizes the distance from
    # the v0, v1, v2 triangle
    v3 = max(vertices, key=lambda v: abs(vecDistanceTriangle((v0, v1, v2), v)))
    # ensure positive orientation
    if vecDistanceTriangle((v0, v1, v2), v3) > 0:
        return [ v0, v1, v2, v3 ]
    else:
        return [ v1, v0, v2, v3 ]


def qhull3d(vertices):
    """Return the faces making up the convex hull of C{vertices}.
    
    @param vertices: The vertices to add to the convex set given by C{faces}.
    @param faces: Optionally, a convex set of faces to start with.

    Test a tetrahedron
    ------------------

    >>> import random
    >>> tetrahedron = [(0,0,0),(1,0,0),(0,1,0),(0,0,1)]
    >>> for i in xrange(200):
    ...     alpha = random.random()
    ...     beta = random.random()
    ...     gamma = 1 - alpha - beta
    ...     if gamma >= 0:
    ...         tetrahedron.append((alpha, beta, gamma))
    >>> verts, faces = qhull3d(tetrahedron)
    >>> (0,0,0) in verts
    True
    >>> (1,0,0) in verts
    True
    >>> (0,1,0) in verts
    True
    >>> (0,0,1) in verts
    True
    >>> len(verts)
    4
    >>> len(faces)
    4

    Test a pyramid
    --------------

    >>> verts, faces = qhull3d([(0,0,0),(1,0,0),(0,1,0),(1,1,0),(0.5,0.5,1)])
    >>> (0,0,0) in verts
    True
    >>> (1,0,0) in verts
    True
    >>> (0,1,0) in verts
    True
    >>> (1,1,0) in verts
    True
    >>> len(verts)
    5
    >>> len(faces)
    6

    Test the unit cube
    ------------------

    >>> import random
    >>> cube = [(0,0,0),(0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,0,1),(1,1,0),(1,1,1)]
    >>> for i in xrange(200):
    ...     cube.append((random.random(), random.random(), random.random()))
    >>> verts, faces = qhull3d(cube)
    >>> len(faces) # 6 faces, written as 12 triangles
    12
    >>> len(verts)
    8

    Test a degenerate shape: unit square
    ------------------------------------
    
    >>> import random
    >>> plane = [(0,0,0),(0,0,1),(0,1,0),(1,1,0)]
    >>> for i in xrange(200):
    ...     plane.append((random.random(), random.random(), 0))
    >>> verts, faces = qhull3d(plane)
    >>> len(verts)
    4
    >>> len(faces)
    2

    Test a random shape
    -------------------

    >>> import random
    >>> shape = []
    >>> for i in xrange(2000):
    ...     vert = (random.random(), random.random(), random.random())
    ...     shape.append(vert)
    >>> verts, faces = qhull3d(shape)
    """
    # find a simplex to start from
    extreme_vertices = basesimplex3d(vertices)

    # construct list of faces of this simplex
    faces = set([ operator.itemgetter(i,j,k)(extreme_vertices)
                  for i, j, k in ((1,0,2), (0,1,3), (0,3,2), (3,1,2)) ])

    # construct list of outer vertices for each face
    outer_vertices = {}
    for face in faces:
        outer = \
            [ (dist, vert)
              for dist, vert in izip( ( vecDistanceTriangle(face, vert)
                                        for vert in vertices ),
                                      vertices )
              if dist > _EPSILON ]
        if outer:
            outer_vertices[face] = outer

    # as long as there are faces with outer vertices
    while outer_vertices:
        # grab a face and its outer vertices
        face, outer = outer_vertices.iteritems().next()
        # calculate pivot point
        pivot = max(outer)[1]
        # add it to the list of extreme vertices
        extreme_vertices.append(pivot)
        # and update the list of faces:
        # 1. calculate visibility of faces to pivot point
        visibility = [ vecDistanceTriangle(otherface, pivot) > _EPSILON
                       for otherface in outer_vertices.iterkeys() ]
        # 2. get list of visible faces
        visible_faces = [ otherface
                          for otherface, visible
                          in izip(outer_vertices.iterkeys(), visibility)
                          if visible ]
        # and list of all vertices associated with visible faces
        visible_outer = reduce(operator.add,
                               [ [ vert
                                   for dist, vert
                                   in outer_vertices[otherface] ]
                                 for otherface in visible_faces ] )
        # 3. find all edges of visible faces
        visible_edges = reduce(operator.add,
                               [ [ operator.itemgetter(i,j)(visible_face)
                                   for i, j in ((0,1),(1,2),(2,0)) ]
                                 for visible_face in visible_faces ], [] )
        # 4. construct horizon: edges that are not shared with another face
        horizon_edges = [ edge for edge in visible_edges
                          if not tuple(reversed(edge)) in visible_edges ]
        # 5. remove visible faces from list
        # this puts a hole inside the face list
        for face in visible_faces:
            faces.remove(face)
            del outer_vertices[face]
        # 6. close face list by adding cone from horizon to pivot
        # also update the outer face list as we go
        for edge in horizon_edges:
            newface = edge + ( pivot, )
            newouter = \
                [ (dist, vert)
                  for dist, vert in izip( ( vecDistanceTriangle(newface, vert)
                                            for vert in visible_outer ),
                                          visible_outer )
                  if dist > _EPSILON ]
            faces.add(newface)
            if newouter:
                outer_vertices[newface] = newouter

    # no face has outer vertices anymore
    # so the convex hull is complete!
    return extreme_vertices, faces

if __name__ == "__main__":
    import doctest
    doctest.testmod()
