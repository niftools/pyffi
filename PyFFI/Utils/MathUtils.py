"""A lightweight library for common vector operations."""

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

from itertools import izip
import operator

def vecSub(vec1, vec2):
    """Vector substraction."""
    return map(operator.sub, vec1, vec2)

def vecDotProduct(vec1, vec2):
    """The vector dot product (any dimension).

    >>> vecDotProduct((1,2,3),(4,-5,6))
    12"""
    return sum(x1 * x2 for x1, x2 in izip(vec1, vec2))

def vecDistance(vec1, vec2):
    """Return distance between two vectors (any dimension).

    >>> vecDistance((1,2,3),(4,-5,6)) # doctest: +ELLIPSIS
    8.185...
    """
    return vecNorm(vecSub(vec1, vec2))

def vecNormal(vec1, vec2, vec3):
    """Returns a vector that is orthogonal on C{triangle}."""
    return vecCrossProduct(vecSub(vec2, vec1), vecSub(vec3, vec1))

def vecDistanceAxis(axis, vec):
    """Return distance between the axis spanned by axis[0] and axis[1] and the
    vector v, in 3 dimensions. Raises ZeroDivisionError if the axis points
    coincide.

    >>> vecDistanceAxis([(0,0,0), (0,0,1)], (0,3.5,0))
    3.5
    >>> vecDistanceAxis([(0,0,0), (1,1,1)], (0,1,0.5)) # doctest: +ELLIPSIS
    0.70710678...
    """
    return vecNorm(vecNormal(axis[0], axis[1], vec)) / vecDistance(*axis)

def vecDistanceTriangle(triangle, vert):
    """Return (signed) distance between the plane spanned by triangle[0],
    triangle[1], and triange[2], and the vector v, in 3 dimensions.

    >>> vecDistanceTriangle([(0,0,0),(1,0,0),(0,1,0)], (0,0,1))
    1.0
    >>> vecDistanceTriangle([(0,0,0),(0,1,0),(1,0,0)], (0,0,1))
    -1.0
    """
    normal = vecNormal(*triangle)
    return vecDotProduct(normal, vecSub(vert, triangle[0])) \
           / vecNorm(normal)

def vecNorm(vec):
    """Norm of a vector (any dimension).

    >>> vecNorm((2,3,4)) # doctest: +ELLIPSIS
    5.3851648...
    """
    return vecDotProduct(vec, vec) ** 0.5

def vecCrossProduct(vec1, vec2):
    """The vector cross product (in 3d).

    >>> vecCrossProduct((1,0,0),(0,1,0))
    (0, 0, 1)
    >>> vecCrossProduct((1,2,3),(4,5,6))
    (-3, 6, -3)
    """
    return (vec1[1] * vec2[2] - vec1[2] * vec2[1],
            vec1[2] * vec2[0] - vec1[0] * vec2[2],
            vec1[0] * vec2[1] - vec1[1] * vec2[0])

if __name__ == "__main__":
    import doctest
    doctest.testmod()
