"""A lightweight library for common vector and matrix operations."""

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

EPSILON = 0.0001

def vecSub(vec1, vec2):
    """Vector substraction."""
    return tuple(x - y for x, y in izip(vec1, vec2))

def vecAdd(vec1, vec2):
    return tuple(x + y for x, y in izip(vec1, vec2))

def vecscalarMul(vec, scalar):
    return tuple(x * scalar for x in vec)

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

def matTransposed(mat):
    """Return the transposed of a nxn matrix.

    >>> matTransposed(((1, 2), (3, 4)))
    ((1, 3), (2, 4))"""
    dim = len(mat)
    return tuple( tuple( mat[i][j]
                         for i in xrange(dim) )
                  for j in xrange(dim) )

def matscalarMul(mat, scalar):
    """Return matrix * scalar."""
    dim = len(mat)
    return tuple( tuple( mat[i][j] * scalar
                         for j in xrange(dim) )
                  for i in xrange(dim) )

def matvecMul(mat, vec):
    """Return matrix * vector."""
    dim = len(mat)
    return tuple( sum( mat[i][j] * vec[j] for j in xrange(dim) )
                  for i in xrange(dim) )

def matMul(mat1, mat2):
    """Return matrix * matrix."""
    dim = len(mat1)
    return tuple( tuple( sum( mat1[i][k] * mat2[k][j]
                              for k in xrange(dim) )
                         for j in xrange(dim) )
                  for i in xrange(dim) )

def matAdd(mat1, mat2):
    """Return matrix + matrix."""
    dim = len(mat1)
    return tuple( tuple( mat1[i][j] + mat2[i][j]
                         for j in xrange(dim) )
                  for i in xrange(dim) )

def matSub(mat1, mat2):
    """Return matrix - matrix."""
    dim = len(mat1)
    return tuple( tuple( mat1[i][j] - mat2[i][j]
                         for j in xrange(dim) )
                  for i in xrange(dim) )

def matCofactor(mat, i, j):
    dim = len(mat)
    return matDeterminant(tuple( tuple( mat[ii][jj]
                                        for jj in xrange(dim)
                                        if jj != j )
                                 for ii in xrange(dim)
                                 if ii != i ))

def matDeterminant(mat):
    """Calculate determinant.

    >>> matDeterminant( ((1,2,3), (4,5,6), (7,8,9)) )
    0
    >>> matDeterminant( ((1,2,4), (3,0,2), (-3,6,2)) )
    36
    """
    dim = len(mat)
    if dim == 0: return 0
    elif dim == 1: return mat[0][0]
    elif dim == 2: return mat[0][0] * mat[1][1] - mat[1][0] * mat[0][1]
    else:
        return sum( (-1 if i&1 else 1) * mat[i][0] * matCofactor(mat, i, 0)
                    for i in xrange(dim) )

#==============================================================================

from types import GeneratorType

class Vector(list):
    """A general purpose vector class."""
    def __init__(self, *args):
        """Vector constructor. Takes either a single list/tuple/generator
        argument, or multiple int, long, float arguments.

        >>> Vector(1,2,3)
        [1, 2, 3]
        >>> Vector("abc") # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        """
        if len(args) == 1 and isinstance(args[0], (list, tuple, GeneratorType)):
            # single list/tuple/generator type
            list.__init__(self, args[0])
        else:
            list.__init__(self, (elem for elem in args))
        for elem in self:
            if not isinstance(elem, (int, long, float)):
                raise TypeError("Vector must consist of scalars.")

    def __add__(self, other):
        """Vector and scalar addition.

        >>> Vector(1,2,3) + Vector(5,4,3)
        [6, 6, 6]
        >>> Vector(1,2,3) + 5
        [6, 7, 8]
        """
        if isinstance(other, Vector):
            return Vector(elem1 + elem2 for elem1, elem2 in izip(self, other))
        elif isinstance(other, (int, long, float)):
            return Vector(elem + other for elem in self)
        else:
            raise TypeError("cannot add %s and %s"
                            % (self.__class__, other.__class__))

    def __radd__(self, other):
        """Scalar plus Vector.

        >>> 5 + Vector(1,2,3)
        [6, 7, 8]
        """
        if isinstance(other, (int, long, float)):
            return Vector(elem + other for elem in self)
        else:
            raise TypeError("cannot add %s and %s"
                            % (other.__class__, self.__class__))

    def __neg__(self):
        """Negation.

        >>> -Vector(1,2,3,4)
        [-1, -2, -3, -4]
        """
        return Vector(-elem for elem in self)
    
    def __sub__(self, other):
        """Vector and scalar substraction.

        >>> Vector(1,2,3) - Vector(5,4,3)
        [-4, -2, 0]
        >>> Vector(1,2,3) - 5
        [-4, -3, -2]
        >>> Vector(1,2,3) - "hi" # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        """
        if isinstance(other, Vector):
            return Vector(elem1 - elem2 for elem1, elem2 in izip(self, other))
        elif isinstance(other, (int, long, float)):
            return Vector(elem - other for elem in self)
        else:
            raise TypeError("cannot substract %s and %s"
                            % (self.__class__, other.__class__))

    def __rsub__(self, other):
        """Scalar minus Vector.

        >>> 5 - Vector(1,2,3)
        [4, 3, 2]
        """
        if isinstance(other, (int, long, float)):
            return Vector(other - elem for elem in self)
        else:
            raise TypeError("cannot substract %s and %s"
                            % (other.__class__, self.__class__))
    def __mul__(self, other):
        """Dot product, scalar product, and matrix product.

        >>> Vector(1,2,3) * Vector(4,-5,6)
        12
        >>> Vector(2,3,4) * 5
        [10, 15, 20]
        >>> Vector(4,-5,6) * LMatrix((1,2,3),(2,3,4),(4,5,6))
        [18, 23, 28]
        >>> Vector(4,-5,6) * LMatrix((1,2,4),(2,3,5),(3,4,6))
        [12, 17, 27]
        >>> RMatrix((1,2,3),(2,3,4),(4,5,6)) * Vector(4,-5,6)
        [12, 17, 27]
        >>> Vector(4,-5,6) * Matrix((1,2,3),(2,3,4),(4,5,6)) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        >>> Vector(4,-5,6) * RMatrix((1,2,3),(2,3,4),(4,5,6)) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        """
        if isinstance(other, Vector):
            return sum(map(operator.mul, self, other))
        elif isinstance(other, LMatrix):
            if len(self) != other._dim_n:
                raise ValueError("cannot multiply %i-vector with %ix%i-matrix"
                                 % (len(self), other._dim_n, other._dim_m))
            return Vector( sum( self[i] * other[i][j]
                                for i in xrange(other._dim_n) )
                           for j in xrange(other._dim_m) )
        elif isinstance(other, (int, long, float)):
            return Vector(other * elem for elem in self)
        else:
            raise TypeError("cannot multiply %s and %s"
                            % (self.__class__, other.__class__))

    def __rmul__(self, other):
        """Scalar times Vector.

        >>> 5 * Vector(2,3,4)
        [10, 15, 20]"""
        if isinstance(other, (int, long, float)):
            return (self * other)
        else:
            raise TypeError("cannot multiply %s and %s"
                            % (other.__class__, self.__class__))

    def cross(self, other):
        """Cross product, for 3 dimensional vectors.

        >>> Vector(1,0,0).cross(Vector(0,1,0))
        [0, 0, 1]
        >>> Vector(1,2,3).cross(Vector(4,5,6))
        [-3, 6, -3]
        >>> Vector(1,2).cross(Vector(4,5,6)) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: ...
        >>> Vector(1,2).cross("hi") # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        """
        if not isinstance(other, Vector):
            raise TypeError("cannot take cross product of %s and %s"
                            % (other.__class__, self.__class__))
        if len(self) != len(other) or len(self) != 3:
            raise ValueError(
                "can only take cross product if both vectors have length 3")
        return Vector(self[1] * other[2] - self[2] * other[1],
                      self[2] * other[0] - self[0] * other[2],
                      self[0] * other[1] - self[1] * other[0])
        

    def __div__(self, other):
        """Divide a Vector by a scalar.

        >>> 0.000000001 + (Vector(2,3,4) / 5.0) # doctest: +ELLIPSIS
        [0.4000..., 0.6000..., 0.8000...]
        """
        if isinstance(other, (int, long, float)):
            return Vector(elem / other for elem in self)
        else:
            raise TypeError("...")

    def norm(self):
        """Norm of the vector.

        >>> Vector(1,2,3).norm() # doctest: +ELLIPSIS
        3.74165738677394...
        """
        return (self * self) ** 0.5

    def normalized(self):
        """Return normalized self. Raise ValueError if the vector
        cannot be normalized.

        >>> x = Vector(1,2,3).normalized()
        >>> x # doctest: +ELLIPSIS
        [0.2672612419124..., 0.5345224838248..., 0.8017837257372...]
        >>> x.norm() + 0.00001 # doctest: +ELLIPSIS
        1.000...
        >>> Vector(0,0,0).normalized() # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: ...
        """
        norm = self.norm()
        if norm < EPSILON:
            raise ValueError('cannot normalize vector %s' % self)
        return Vector(elem / norm for elem in self)

class Matrix(list):
    """A general purpose matrix base class, without vector multiplication.
    For matrices that support vector multiplication, use LMatrix, RMatrix, or
    LRMatrix."""
    # note: all multiplication code (L/R)Matrix * something is implemented in
    # __mul__
    
    def __init__(self, *args):
        """Initialize matrix from row vectors.

        >>> Matrix((1,2,3),(4,5,6),(7,8,9))
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        >>> Matrix(( row for row in xrange(i, i + 3) ) for i in xrange(3))
        [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        """
        if len(args) == 1 and isinstance(args[0], (list, tuple, GeneratorType)):
            # single list/tuple/generator type
            list.__init__(self, (list(row) for row in args[0]))
        else:
            list.__init__(self, ( list( elem for elem in row )
                                  for row in args ))
        self._dim_n = len(self)
        self._dim_m = len(self[0]) if self._dim_n else 0
        for row in self:
            if len(row) != self._dim_m:
                raise ValueError("all rows must have the same length")
        for row in self:
            for elem in row:
                if not isinstance(elem, (int, long, float)):
                    raise TypeError("Matrix must consist of scalars.")

    def __add__(self, other):
        """Matrix and scalar addition.

        >>> Matrix((1,2,3),(2,3,4),(4,5,6)) + Matrix((3,2,1),(2,1,0),(1,2,3))
        [[4, 4, 4], [4, 4, 4], [5, 7, 9]]
        >>> Matrix((1,2,3),(2,3,4)) + 5
        [[6, 7, 8], [7, 8, 9]]
        """
        if isinstance(other, Matrix):
            # type check
            if not self.__class__ is other.__class__:
                raise TypeError("cannot add %s and %s"
                                % (other.__class__, self.__class__))
            # dimension check
            if self._dim_n != other._dim_n or self._dim_m != other._dim_m:
                raise ValueError(
                    "cannot add matrices with different dimensions")
            return self.__class__( ( elem1 + elem2
                                     for elem1, elem2 in izip(row1, row2) )
                                   for row1, row2 in izip(self, other) )
        elif isinstance(other, (int, long, float)):
            return self.__class__( ( elem + other for elem in row )
                                   for row in self )
        else:
            raise TypeError("cannot add %s and %s"
                            % (self.__class__, other.__class__))

    def __radd__(self, other):
        """Scalar plus Matrix.

        >>> 5 + Matrix((1,2,3),(2,3,4),(4,5,6))
        [[6, 7, 8], [7, 8, 9], [9, 10, 11]]
        """
        if isinstance(other, (int, long, float)):
            return self.__class__( ( elem + other for elem in row )
                                   for row in self )
        else:
            raise TypeError("cannot add %s and %s"
                            % (other.__class__, self.__class__))

    def __sub__(self, other):
        """Matrix and scalar substraction.

        >>> Matrix((1,2,3),(2,3,4),(4,5,6)) - Matrix((3,2,1),(2,1,0),(1,2,3))
        [[-2, 0, 2], [0, 2, 4], [3, 3, 3]]
        >>> Matrix((1,2,3),(2,3,4)) - 5
        [[-4, -3, -2], [-3, -2, -1]]
        """
        if isinstance(other, Matrix):
            # type check
            if not self.__class__ is other.__class__:
                raise TypeError("cannot add %s and %s"
                                % (other.__class__, self.__class__))
            # dimension check
            if self._dim_n != other._dim_n or self._dim_m != other._dim_m:
                raise ValueError(
                    "cannot substract matrices with different dimensions")
            return self.__class__( ( elem1 - elem2
                                   for elem1, elem2 in izip(row1, row2) )
                           for row1, row2 in izip(self, other) )
        elif isinstance(other, (int, long, float)):
            return self.__class__( ( elem - other for elem in row )
                                   for row in self )
        else:
            raise TypeError("cannot add %s and %s"
                            % (self.__class__, other.__class__))

    def __rsub__(self, other):
        """Scalar minus Matrix.

        >>> 5 - Matrix((1,2,3),(2,3,4),(4,5,6))
        [[4, 3, 2], [3, 2, 1], [1, 0, -1]]
        """
        if isinstance(other, (int, long, float)):
            return self.__class__( ( other - elem for elem in row )
                                   for row in self )
        else:
            raise TypeError("cannot add %s and %s"
                            % (other.__class__, self.__class__))

    def __mul__(self, other):
        """Matrix times scalar, Vector, or Matrix.

        >>> LMatrix((1,2,3),(2,3,4),(4,5,6)) * LMatrix((1,2,3),(2,3,4),(4,5,6))
        [[17, 23, 29], [24, 33, 42], [38, 53, 68]]
        >>> Matrix((1,2,3),(2,3,4),(4,5,6)) * Vector(4,-5,6) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        >>> LMatrix((1,2,3),(2,3,4),(4,5,6)) * Vector(4,-5,6) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        >>> Matrix((1,2,3),(2,3,4),(4,5,6)) * 5
        [[5, 10, 15], [10, 15, 20], [20, 25, 30]]"""
        if isinstance(other, Matrix):
            # what should be the resulting class?
            if isinstance(self, LMatrix) and isinstance(other, LMatrix):
                cls = LMatrix
            elif isinstance(self, RMatrix) and isinstance(other, RMatrix):
                cls = RMatrix
            elif isinstance(self, LMatrix) and isinstance(other, RMatrix):
                cls = LRMatrix
            elif isinstance(self, LMatrix) and isinstance(other, LRMatrix):
                cls = LRMatrix
            elif isinstance(self, LRMatrix) and isinstance(other, RMatrix):
                cls = LRMatrix
            else:
                raise TypeError("cannot multiply %s and %s"
                                % (self.__class__, other.__class__))
            # check dimensions
            if self._dim_m != other._dim_n:
                raise ValueError(
                    "cannot multiply %ix%i-matrix with %ix%i-matrix"
                    % (self._dim_n, self._dim_m, other._dim_n, other._dim_m))
            # do the multiplication
            return cls( ( sum(self[i][k] * other[k][j]
                              for k in xrange(self._dim_m) )
                          for j in xrange(other._dim_m) )
                        for i in xrange(self._dim_n) )
        elif isinstance(self, RMatrix) and isinstance(other, Vector):
            if len(other) != self._dim_n:
                raise ValueError("cannot multiply %ix%i-matrix and %i vector"
                                 % (self._dim_n, self._dim_m, len(other)))
            return Vector( sum( self[i][j] * other[j]
                                for j in xrange(self._dim_m) )
                           for i in xrange(self._dim_n) )
        elif isinstance(other, (int, long, float)):
            return self.__class__( ( other * elem for elem in row )
                                   for row in self )
        else:
            raise TypeError("cannot multiply %s and %s"
                            % (self.__class__, other.__class__))

    def __rmul__(self, other):
        """Scalar times Matrix.

        >>> 5 * Matrix((1,2,3),(2,3,4),(4,5,6))
        [[5, 10, 15], [10, 15, 20], [20, 25, 30]]
        """
        if isinstance(other, (int, long, float)):
            return (self * other)
        else:
            raise TypeError("cannot multiply %s and %s"
                            % (other.__class__, self.__class__))

class LMatrix(Matrix):
    """A general purpose matrix class, with left vector multiplication. Use
    for linear transforms."""
    # the left multiplication is implemented in the Vector class

class RMatrix(Matrix):
    """A general purpose matrix class, with vector multiplication from the
    right. Use for linear transforms."""
    # the right multiplication is implemented in the Matrix class

class LRMatrix(Matrix):
    """A general purpose matrix class, with vector multiplication from both
    sides. Use for bilinear forms (such as inertia tensors)."""
    def product(self, vec1, vec2):
        return sum( sum( vec1[i] * self[i][j]
                         for i in xrange(self._dim_n) )
                    * vec2[j]
                    for j in xrange(self._dim_m) )

if __name__ == "__main__":
    import doctest
    doctest.testmod()
