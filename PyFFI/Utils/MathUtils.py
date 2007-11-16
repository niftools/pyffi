"""A lightweight library for common vector operations."""

from itertools import izip
import operator

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
    diff = map(operator.sub, vec1, vec2)
    return vecDotProduct(diff, diff) ** 0.5

def vecDistanceAxis(axis, vec):
    """Return distance between the axis spanned by axis[0] and axis[1] and the
    vector v, in 3 dimensions.

    >>> vecDistanceAxis([(0,0,0), (0,0,1)], (0,3.5,0))
    3.5
    >>> vecDistanceAxis([(0,0,0), (1,1,1)], (0,1,0.5)) # doctest: +ELLIPSIS
    0.70710678...
    """
    return (vecNorm(vecCrossProduct(map(operator.sub, axis[1], axis[0]),
                                    map(operator.sub, axis[0], vec)))
            / vecNorm(map(operator.sub, axis[1], axis[0])))

def vecDistanceTriangle(triangle, v):
    """Return (signed) distance between the plane spanned by triangle[0],
    triangle[1], and triange[2], and the vector v, in 3 dimensions.

    >>> vecDistanceTriangle([(0,0,0),(1,0,0),(0,1,0)], (0,0,1))
    -1.0
    >>> vecDistanceTriangle([(0,0,0),(0,1,0),(1,0,0)], (0,0,1))
    1.0
    """
    normal = vecCrossProduct(map(operator.sub, triangle[2], triangle[0]),
                             map(operator.sub, triangle[1], triangle[0]))
    return vecDotProduct(normal, map(operator.sub, v, triangle[0])) \
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
