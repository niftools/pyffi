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
    inertia_yy = inertia_matrix[0][0]
    inertia_zz = 0.5 * mass * (radius ** 2)

    return mass,  ( ( inertia_xx, 0, 0 ),
                    ( 0, inertia_yy, 0 ),
                    ( 0, 0, inertia_zz ) )

# references:
#
# Jonathan Blow, Atman J Binstock
# "How to find the inertia tensor (or other mass properties) of a 3D solid body represented by a triangle mesh"
# http://number-none.com/blow/inertia/bb_inertia.doc
#
# David Eberly
# "Polyhedral Mass Properties (Revisited)"
# http://www.geometrictools.com//LibPhysics/RigidBody/Wm4PolyhedralMassProperties.cpp
def getMassCenterInertiaPolyhedron(vertices, triangles, density = 1,
                                   bodycoords = True):
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
    >>> sphere = []
    >>> for i in xrange(0, 50):
    ...     theta = i * 2 * math.pi / 50
    ...     s, c = math.sin(theta), math.cos(theta)
    ...     for j in xrange(1, 50):
    ...         h = j / 25.0 - 1.0
    ...         sphere.append((2*s, 2*c, 2*h)) # construct sphere of radius 2
    >>> sphere.append((0,0,2))
    >>> sphere.append((0,0,-2))
    >>> vertices, triangles = QuickHull.qhull3d(sphere)
    >>> mass, center, inertia = getMassCenterInertiaPolyhedron(
    ...     vertices, triangles, density = 3)
    >>> mass
    100.53096...
    >>> sum(abs(x) for x in center) < 0.01 # is center at origin?
    True
    >>> inertia[0][0]
    160.84954...
    """

    ## Blow and Binstock's method

##    # covariance matrix of the canonical tetrahedron
##    # (0,0,0),(1,0,0),(0,1,0),(0,0,1)
##    covariance_canonical = ( (1/60.0 , 1/120.0, 1/120.0 ),
##                             (1/120.0, 1/60.0 , 1/120.0 ),
##                             (1/120.0, 1/120.0, 1/60.0  ) )
##
##    covariances = []
##    masses = []
##    centers = []
##
##    # for each triangle
##    # construct a tetrahedron from triangle + (0,0,0)
##    # find its matrix, mass, and center
##    # and update the matrix accordingly
##    for triangle in triangles:
##        # get vertices
##        vert0, vert1, vert2 = operator.itemgetter(*triangle)(vertices)
##
##        # construct a transform matrix that converts the canonical tetrahedron
##        # into (0,0,0),vert0,vert1,vert2
##        transform_transposed = ( vert0, vert1, vert2 )
##        transform = matTransposed(transform_transposed)
##
##        # we shall be needing the determinant more than once, so
##        # precalculate it
##        determinant = matDeterminant(transform)
##
##        # find the covariance matrix of the transformed tetrahedron
##        covariances.append(
##            matscalarMul(
##                reduce(matMul,
##                       (transform, covariance_canonical, transform_transposed)),
##                determinant))
##
##        # find mass
##        masses.append(determinant / 6.0) # assume density = 1, fixed below
##
##        # find center of gravity of the tetrahedron
##        centers.append(tuple( 0.25 * sum(vert[i]
##                                         for vert in (vert0, vert1, vert2))
##                              for i in xrange(3) ))
##        print transform_transposed, centers[-1], masses[-1]
##
##    # accumulate the results
##    total_covariance = reduce(matAdd, covariances)
##    total_mass = density * sum(masses) # now take into account the density
##    total_center = reduce(vecAdd, ( vecscalarMul(center, mass / total_mass)
##                                    for center, mass
##                                    in izip(centers, masses)))
##
##    # translate covariance to center of gravity
##    ...
##    # convert covariance matrix into inertia tensor
##    ...
##    #return total_mass, total_center, total_inertia

    ## Eberly's method (very optimized hence faster than above method
    ## although quite a bit harder to understand):

    # order:  1, x, y, z, x^2, y^2, z^2, xy, yz, zx
    afIntegral = [ 0.0 for i in xrange(10) ]

    for idx0, idx1, idx2 in triangles:
        # get the vertices of the current triangle
        kV0, kV1, kV2 = vertices[idx0], vertices[idx1], vertices[idx2]
        # get normal of the triangle
        kN = vecNormal(kV0, kV1, kV2)

        # compute integral terms
        fTmp0 = kV0[0] + kV1[0]
        fF1x = fTmp0 + kV2[0]
        fTmp1 = kV0[0]*kV0[0]
        fTmp2 = fTmp1 + kV1[0]*fTmp0
        fF2x = fTmp2 + kV2[0]*fF1x
        fF3x = kV0[0]*fTmp1 + kV1[0]*fTmp2 + kV2[0]*fF2x
        fG0x = fF2x + kV0[0]*(fF1x + kV0[0])
        fG1x = fF2x + kV1[0]*(fF1x + kV1[0])
        fG2x = fF2x + kV2[0]*(fF1x + kV2[0])

        fTmp0 = kV0[1] + kV1[1]
        fF1y = fTmp0 + kV2[1]
        fTmp1 = kV0[1]*kV0[1]
        fTmp2 = fTmp1 + kV1[1]*fTmp0
        fF2y = fTmp2 + kV2[1]*fF1y
        fF3y = kV0[1]*fTmp1 + kV1[1]*fTmp2 + kV2[1]*fF2y
        fG0y = fF2y + kV0[1]*(fF1y + kV0[1])
        fG1y = fF2y + kV1[1]*(fF1y + kV1[1])
        fG2y = fF2y + kV2[1]*(fF1y + kV2[1])

        fTmp0 = kV0[2] + kV1[2]
        fF1z = fTmp0 + kV2[2]
        fTmp1 = kV0[2]*kV0[2]
        fTmp2 = fTmp1 + kV1[2]*fTmp0
        fF2z = fTmp2 + kV2[2]*fF1z
        fF3z = kV0[2]*fTmp1 + kV1[2]*fTmp2 + kV2[2]*fF2z
        fG0z = fF2z + kV0[2]*(fF1z + kV0[2])
        fG1z = fF2z + kV1[2]*(fF1z + kV1[2])
        fG2z = fF2z + kV2[2]*(fF1z + kV2[2])

        # update integrals
        afIntegral[0] += kN[0]*fF1x
        afIntegral[1] += kN[0]*fF2x
        afIntegral[2] += kN[1]*fF2y
        afIntegral[3] += kN[2]*fF2z
        afIntegral[4] += kN[0]*fF3x
        afIntegral[5] += kN[1]*fF3y
        afIntegral[6] += kN[2]*fF3z
        afIntegral[7] += kN[0]*(kV0[1]*fG0x + kV1[1]*fG1x + kV2[1]*fG2x)
        afIntegral[8] += kN[1]*(kV0[2]*fG0y + kV1[2]*fG1y + kV2[2]*fG2y)
        afIntegral[9] += kN[2]*(kV0[0]*fG0z + kV1[0]*fG1z + kV2[0]*fG2z)

    afIntegral[0] /= 6.0
    afIntegral[1] /= 24.0
    afIntegral[2] /= 24.0
    afIntegral[3] /= 24.0
    afIntegral[4] /= 60.0
    afIntegral[5] /= 60.0
    afIntegral[6] /= 60.0
    afIntegral[7] /= 120.0
    afIntegral[8] /= 120.0
    afIntegral[9] /= 120.0

    # mass
    rfMass = density * afIntegral[0]

    # center of mass
    rkCenter = (afIntegral[1] / afIntegral[0],
                afIntegral[2] / afIntegral[0],
                afIntegral[3] / afIntegral[0])

    # inertia relative to world origin
    rkInertia = [ [ 0.0 for i in xrange(3) ] for j in xrange(3) ]
    rkInertia[0][0] = density * (afIntegral[5] + afIntegral[6])
    rkInertia[0][1] = density * (-afIntegral[7])
    rkInertia[0][2] = density * (-afIntegral[9])
    rkInertia[1][0] = rkInertia[0][1]
    rkInertia[1][1] = density * (afIntegral[4] + afIntegral[6])
    rkInertia[1][2] = density * (-afIntegral[8])
    rkInertia[2][0] = rkInertia[0][2]
    rkInertia[2][1] = rkInertia[1][2]
    rkInertia[2][2] = density * (afIntegral[4] + afIntegral[5])

    # inertia relative to center of mass
    if bodycoords:
        rkInertia[0][0] -= rfMass*(rkCenter[1]*rkCenter[1]
                                   + rkCenter[2]*rkCenter[2])
        rkInertia[0][1] += rfMass*rkCenter[0]*rkCenter[1]
        rkInertia[0][2] += rfMass*rkCenter[2]*rkCenter[0]
        rkInertia[1][0] = rkInertia[0][1]
        rkInertia[1][1] -= rfMass*(rkCenter[2]*rkCenter[2]
                                   + rkCenter[0]*rkCenter[0])
        rkInertia[1][2] += rfMass*rkCenter[1]*rkCenter[2]
        rkInertia[2][0] = rkInertia[0][2]
        rkInertia[2][1] = rkInertia[1][2]
        rkInertia[2][2] -= rfMass*(rkCenter[0]*rkCenter[0]
                                   + rkCenter[1]*rkCenter[1])

    return rfMass, rkCenter, tuple(tuple(x for x in row) for row in rkInertia)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
