"""Calculate the mass, center of gravity, and inertia matrix for common
shapes."""

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

import math
from MathUtils import *

# see http://en.wikipedia.org/wiki/List_of_moment_of_inertia_tensors

def getMassInertiaSphere(radius, density = 1):
    """Return mass and inertia matrix for a sphere of given radius and
    density.

    >>> mass, inertia_matrix = getMassInertiaSphere(2.0, 3.0)
    >>> mass # doctest: +ELLIPSIS
    100.53096...
    >>> inertia_matrix[0][0] # doctest: +ELLIPSIS
    160.84954..."""
    mass = density * (4 * math.pi * (radius ** 3)) / 3
    inertia = (2 * mass * (radius ** 2)) / 5

    return mass, tuple( tuple( (inertia if i == j else 0)
                               for i in xrange(3) )
                        for j in xrange(3) )

def getMassInertiaBox(size, density = 1):
    """Return mass and inertia matrix for a box of given size and
    density.

    >>> mass, inertia = getMassInertiaBox((1.0, 2.0, 3.0), 4.0)
    >>> mass
    24.0
    >>> inertia
    ((26.0, 0, 0), (0, 20.0, 0), (0, 0, 10.0))
    """
    assert(len(size) == 3) # debug
    mass = density * reduce(operator.mul, size)
    tmp = tuple(mass * (length ** 2) / 12.0 for length in size)
    return mass, ( ( tmp[1] + tmp[2], 0, 0 ),
                   ( 0, tmp[2] + tmp[0], 0 ),
                   ( 0, 0, tmp[0] + tmp[1] ) )

def getMassInertiaCapsule(length, radius, density = 1):
    # cylinder + caps, and caps have volume of a sphere
    mass = density * (length * math.pi * (radius ** 2)
                      + (4 * math.pi * (radius ** 3)) / 3)

    # approximate by cylinder
    # TODO: also include the caps into the inertia matrix
    inertia_xx = mass * (3 * (radius ** 2) + (length ** 2)) / 12.0
    inertia_yy = inertia_xx
    inertia_zz = 0.5 * mass * (radius ** 2)

    return mass,  ( ( inertia_xx, 0, 0 ),
                    ( 0, inertia_yy, 0 ),
                    ( 0, 0, inertia_zz ) )

#
# References
# ----------
#
# Jonathan Blow, Atman J Binstock
# "How to find the inertia tensor (or other mass properties) of a 3D solid body represented by a triangle mesh"
# http://number-none.com/blow/inertia/bb_inertia.doc
#
# David Eberly
# "Polyhedral Mass Properties (Revisited)"
# http://www.geometrictools.com//LibPhysics/RigidBody/Wm4PolyhedralMassProperties.pdf
#
# The function is an implementation of the Blow and Binstock algorithm
def getMassCenterInertiaPolyhedron(vertices, triangles, density = 1):
    """Return mass, center of gravity, and inertia matrix for a polyhedron.

    >>> import QuickHull
    >>> box = [(0,0,0),(1,0,0),(0,2,0),(0,0,3),(1,2,0),(0,2,3),(1,0,3),(1,2,3)]
    >>> vertices, triangles = QuickHull.qhull3d(box)
    >>> mass, center, inertia = getMassCenterInertiaPolyhedron(
    ...     vertices, triangles, density = 4)
    >>> mass
    24.0
    >>> center
    (0.5, 1.0, 1.5)
    >>> inertia
    ((26.0, 0.0, 0.0), (0.0, 20.0, 0.0), (0.0, 0.0, 10.0))
    >>> poly = [(3,0,0),(0,3,0),(-3,0,0),(0,-3,0),(0,0,3),(0,0,-3)] # very rough approximation of a sphere of radius 2
    >>> vertices, triangles = QuickHull.qhull3d(poly)
    >>> mass, center, inertia = getMassCenterInertiaPolyhedron(
    ...     vertices, triangles, density = 3)
    >>> mass
    108.0
    >>> center
    (0.0, 0.0, 0.0)
    >>> abs(inertia[0][0] - 194.4) < 0.0001
    True
    >>> abs(inertia[1][1] - 194.4) < 0.0001
    True
    >>> abs(inertia[2][2] - 194.4) < 0.0001
    True
    >>> abs(inertia[0][1]) < 0.0001
    True
    >>> abs(inertia[0][2]) < 0.0001
    True
    >>> abs(inertia[1][2]) < 0.0001
    True
    >>> sphere = []
    >>> N = 10
    >>> for j in xrange(-N+1, N):
    ...     theta = j * 0.5 * math.pi / N
    ...     st, ct = math.sin(theta), math.cos(theta)
    ...     M = max(3, int(ct * 2 * N + 0.5))
    ...     for i in xrange(0, M):
    ...         phi = i * 2 * math.pi / M
    ...         s, c = math.sin(phi), math.cos(phi)
    ...         sphere.append((2*s*ct, 2*c*ct, 2*st)) # construct sphere of radius 2
    >>> sphere.append((0,0,2))
    >>> sphere.append((0,0,-2))
    >>> vertices, triangles = QuickHull.qhull3d(sphere)
    >>> mass, center, inertia = getMassCenterInertiaPolyhedron(
    ...     vertices, triangles, density = 3)
    >>> abs(mass - 100.53) < 10
    True
    >>> sum(abs(x) for x in center) < 0.01 # is center at origin?
    True
    >>> abs(inertia[0][0] - 160.84) < 10
    True
    """

    # 120 times the covariance matrix of the canonical tetrahedron
    # (0,0,0),(1,0,0),(0,1,0),(0,0,1)
    covariance_canonical_120 = ( (2, 1, 1),
                                 (1, 2, 1),
                                 (1, 1, 2) )

    covariances_120 = []
    masses = []
    centers = []

    # for each triangle
    # construct a tetrahedron from triangle + (0,0,0)
    # find its matrix, mass, and center (for density = 1, will be corrected at
    # the end of the algorithm)
    for triangle in triangles:
        # get vertices
        vert0, vert1, vert2 = operator.itemgetter(*triangle)(vertices)

        # construct a transform matrix that converts the canonical tetrahedron
        # into (0,0,0),vert0,vert1,vert2
        transform_transposed = ( vert0, vert1, vert2 )
        transform = matTransposed(transform_transposed)

        # we shall be needing the determinant more than once, so
        # precalculate it
        determinant = matDeterminant(transform)

        # find 120 times the covariance matrix of the transformed tetrahedron
        # C' = det(A) * A * C * A^T
        covariances_120.append(
            matscalarMul(
                reduce(matMul,
                       (transform,
                        covariance_canonical_120,
                        transform_transposed)),
                determinant))

        # find mass
        # m = det(A)
        masses.append(determinant / 6.0)

        # find center of gravity of the tetrahedron
        centers.append(tuple( 0.25 * sum(vert[i]
                                         for vert in (vert0, vert1, vert2))
                              for i in xrange(3) ))

    # accumulate the results and correct the covariance scale
    total_covariance = reduce(matAdd, covariances_120)
    total_covariance = matscalarMul(total_covariance, 1/120.0)
    total_mass = sum(masses)
    if total_mass < 0.0001:
        # shape is too thin
        print "WARNING: shape has almost zero mass"
        return 0, (0,0,0), tuple(tuple(0 for i in xrange(3))
                                  for j in xrange(3))
    total_center = reduce(vecAdd, ( vecscalarMul(center, mass / total_mass)
                                    for center, mass
                                    in izip(centers, masses)))

    # translate covariance to center of gravity:
    # C' = C - m * ( x dx^T + dx x^T + dx dx^T )
    # with x the translation vector and dx the center of gravity
    translate_correction = matscalarMul(tuple(tuple(x * y
                                                    for x in total_center)
                                              for y in total_center),
                                        total_mass)
    total_covariance = matSub(total_covariance, translate_correction)
    
    # convert covariance matrix into inertia tensor
    trace = sum(total_covariance[i][i] for i in xrange(3))
    trace_matrix = tuple(tuple((trace if i == j else 0)
                               for i in xrange(3))
                         for j in xrange(3))
    total_inertia = matSub(trace_matrix, total_covariance)

    # correct for given density
    total_inertia = matscalarMul(total_inertia, density)
    total_mass *= density

if __name__ == "__main__":
    import doctest
    doctest.testmod()
