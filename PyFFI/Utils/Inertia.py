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
from PyFFI.Utils.MathUtils import vecCrossProduct

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

    inertia_matrix = [ [ 0.0 for i in xrange(3) ] for j in xrange(3) ]
    inertia_matrix[0][0] = inertia
    inertia_matrix[1][1] = inertia
    inertia_matrix[2][2] = inertia

    return mass, inertia_matrix

def getMassInertiaBox(size, density = 1):
    """Return mass and inertia matrix for a box of given size and
    density.

    >>> mass, inertia_matrix = getMassInertiaBox((1.0, 2.0, 3.0), 4.0)
    >>> mass # doctest: +ELLIPSIS
    24.0...
    >>> inertia_matrix[0][0] # doctest: +ELLIPSIS
    26.0
    """
    assert(len(size) == 3) # debug
    mass = density * size[0] * size[1] * size[2]
    tmp = map(lambda dim: mass * (dim ** 2) / 12.0, size)
    
    inertia_matrix = [ [ 0.0 for i in xrange(3) ] for j in xrange(3) ]
    inertia_matrix[0][0] = tmp[1] + tmp[2]
    inertia_matrix[1][1] = tmp[2] + tmp[0]
    inertia_matrix[2][2] = tmp[0] + tmp[1]
    return mass, inertia_matrix

def getMassInertiaCapsule(length, radius, density = 1):
    # cylinder + caps, and caps have volume of a sphere
    mass = density * (length * math.pi * (radius ** 2)
                      + (4 * math.pi * (radius ** 3)) / 3)

    # approximate by cylinder
    # TODO: also include the caps into the inertia matrix
    inertia_matrix = [ [ 0.0 for i in xrange(3) ] for j in xrange(3) ]
    inertia_matrix[0][0] = mass * (3 * (radius ** 2) + (length ** 2)) / 12.0
    inertia_matrix[1][1] = inertia_matrix[0][0]
    inertia_matrix[2][2] = 0.5 * mass * (radius ** 2)

    return mass, inertia_matrix

# ported from
# http://www.geometrictools.com//LibPhysics/RigidBody/Wm4PolyhedralMassProperties.cpp

def getMassCenterInertiaPolyhedron(vertices, triangles, density = 1,
                                   bodycoords = False):
    """Return mass, center of gravity, and inertia matrix for a polyhedron.

    >>> getMassCenterInertiaPolyhedron(
    ...     [(0,0,0),(1,0,0),(0,2,0),(0,0,3),(1,2,0),(0,2,3),(1,0,3),(1,2,3)],
    ...     [(0,1,2),()])"""
    # order:  1, x, y, z, x^2, y^2, z^2, xy, yz, zx
    afIntergral = [ 0.0 for i in xrange(10) ]

    for idx0, idx1, idx2 in triangles:
        # get the vertices of the current triangle
        kV0, kV1, kV2 = vertices[idx0], vertices[idx1], vertices[idx2]
        # get cross product of edges
        kV1mV0 = map(operator.sub, kV1, kV0)
        kV2mV0 = map(operator.sub, kV2, kV0)
        kN = vecCrossProduct3d(kV1mV0, kV2mV0)

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

    afIntegral[0] /= 6
    afIntegral[1] /= 24
    afIntegral[2] /= 24
    afIntegral[3] /= 24
    afIntegral[4] /= 60
    afIntegral[5] /= 60
    afIntegral[6] /= 60
    afIntegral[7] /= 120
    afIntegral[8] /= 120
    afIntegral[9] /= 120

    # mass
    rfMass = afIntegral[0]

    # center of mass
    rkCenter = (afIntegral[1],afIntegral[2],afIntegral[3])

    # inertia relative to world origin
    rkInertia = [ [ 0.0 for i in xrange(3) ] for j in xrange(3) ]
    rkInertia[0][0] = afIntegral[5] + afIntegral[6]
    rkInertia[0][1] = -afIntegral[7]
    rkInertia[0][2] = -afIntegral[9]
    rkInertia[1][0] = rkInertia[0][1]
    rkInertia[1][1] = afIntegral[4] + afIntegral[6]
    rkInertia[1][2] = -afIntegral[8]
    rkInertia[2][0] = rkInertia[0][2]
    rkInertia[2][1] = rkInertia[1][2]
    rkInertia[2][2] = afIntegral[4] + afIntegral[5]

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

    return rfMass, rkCenter, rkInertia

if __name__ == "__main__":
    import doctest
    doctest.testmod()
