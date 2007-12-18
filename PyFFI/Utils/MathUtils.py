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

from types import GeneratorType

class Vector(tuple):
    """A general purpose vector class."""
    def __new__(cls, *args):
        """Vector constructor. Takes either a single list/tuple/generator
        argument, or multiple int, long, float arguments.

        >>> Vector(1,2,3)
        (1, 2, 3)
        >>> Vector("abc") # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        """
        if len(args) == 1 and isinstance(args[0], (list, tuple, GeneratorType)):
            # single list/tuple/generator type
            vec = tuple.__new__(cls, args[0])
        else:
            vec = tuple.__new__(cls, (elem for elem in args))
        return vec
    
    def __init__(self, *args):
        for elem in self:
            if not isinstance(elem, (int, long, float)):
                raise TypeError("Vector must consist of scalars.")

    def __add__(self, other):
        """Vector and scalar addition.

        >>> Vector(1,2,3) + Vector(5,4,3)
        (6, 6, 6)
        >>> Vector(1,2,3) + 5
        (6, 7, 8)
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
        (6, 7, 8)
        """
        if isinstance(other, (int, long, float)):
            return Vector(elem + other for elem in self)
        else:
            raise TypeError("cannot add %s and %s"
                            % (other.__class__, self.__class__))

    def __neg__(self):
        """Negation.

        >>> -Vector(1,2,3,4)
        (-1, -2, -3, -4)
        """
        return Vector(-elem for elem in self)
    
    def __sub__(self, other):
        """Vector and scalar substraction.

        >>> Vector(1,2,3) - Vector(5,4,3)
        (-4, -2, 0)
        >>> Vector(1,2,3) - 5
        (-4, -3, -2)
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
        (4, 3, 2)
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
        (10, 15, 20)
        >>> Vector(4,-5,6) * LMatrix((1,2,3),(2,3,4),(4,5,6))
        (18, 23, 28)
        >>> Vector(4,-5,6) * LMatrix((1,2,4),(2,3,5),(3,4,6))
        (12, 17, 27)
        >>> RMatrix((1,2,3),(2,3,4),(4,5,6)) * Vector(4,-5,6)
        (12, 17, 27)
        >>> Vector(1, 1) * LMatrix((0.5,0.5,0), (0.5,-0.5,0), (7,8,1), affine = True)
        (8.0, 8.0)
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
            if not other._affine:
                # linear transform
                if len(self) != other._dim_n:
                    raise ValueError(
                        "cannot multiply %i-vector with %ix%i-matrix"
                        % (len(self), other._dim_n, other._dim_m))
                return Vector( sum( self[i] * other[i][j]
                                    for i in xrange(other._dim_n) )
                               for j in xrange(other._dim_m) )
            else:
                # affine transform
                if len(self) + 1 != other._dim_n:
                    raise ValueError(
                        "cannot multiply %i-vector with affine %ix%i-matrix"
                        % (len(self), other._dim_n, other._dim_m))
                return Vector( sum( ( self[i] * other[i][j]
                                      for i in xrange(other._dim_n - 1) ),
                                    other[-1][j] )
                               for j in xrange(other._dim_m - 1) )
        elif isinstance(other, (int, long, float)):
            return Vector(other * elem for elem in self)
        else:
            raise TypeError("cannot multiply %s and %s"
                            % (self.__class__, other.__class__))

    def __rmul__(self, other):
        """Scalar times Vector.

        >>> 5 * Vector(2,3,4)
        (10, 15, 20)"""
        if isinstance(other, (int, long, float)):
            return (self * other)
        else:
            raise TypeError("cannot multiply %s and %s"
                            % (other.__class__, self.__class__))

    def crossProduct(self, other):
        """Cross product, for 3 dimensional vectors.

        >>> Vector(1,0,0).crossProduct(Vector(0,1,0))
        (0, 0, 1)
        >>> Vector(1,2,3).crossProduct(Vector(4,5,6))
        (-3, 6, -3)
        >>> Vector(1,2).crossProduct(Vector(4,5,6)) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: ...
        >>> Vector(1,2).crossProduct("hi") # doctest: +ELLIPSIS
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

    def getNormal(self, vec2, vec3):
        """Return normal spanned by self, vec2, vec3."""
        return (vec2 - self).crossProduct(vec3 - self)

    def tensorProduct(self, other):
        """Tensor product.

        >>> Vector(1,0,0).tensorProduct(Vector(0,1))
        ((0, 1), (0, 0), (0, 0))
        >>> Vector(1,2,3).tensorProduct(Vector(4,5,6))
        ((4, 5, 6), (8, 10, 12), (12, 15, 18))
        """
        if not isinstance(other, Vector):
            raise TypeError("cannot take tensor product of %s and %s"
                            % (other.__class__, self.__class__))
        return LRMatrix( ( elem1 * elem2 for elem2 in other )
                         for elem1 in self )
        
    def __div__(self, other):
        """Divide a Vector by a scalar.

        >>> 0.000000001 + (Vector(2,3,4) / 5.0) # doctest: +ELLIPSIS
        (0.4000..., 0.6000..., 0.8000...)
        """
        if isinstance(other, (int, long, float)):
            return Vector(elem / other for elem in self)
        else:
            raise TypeError("...")

    def getNorm(self):
        """Norm of the vector.

        >>> Vector(2,3,4).getNorm() # doctest: +ELLIPSIS
        5.3851648...
        >>> Vector(1,2,3).getNorm() # doctest: +ELLIPSIS
        3.74165738677394...
        """
        return (self * self) ** 0.5

    def getNormalized(self):
        """Return normalized self. Raise ValueError if the vector
        cannot be normalized.

        >>> x = Vector(1,2,3).getNormalized()
        >>> x # doctest: +ELLIPSIS
        (0.2672612419124..., 0.5345224838248..., 0.8017837257372...)
        >>> x.getNorm() + 0.00001 # doctest: +ELLIPSIS
        1.000...
        >>> Vector(0,0,0).getNormalized() # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: ...
        """
        norm = self.getNorm()
        if norm < EPSILON:
            raise ValueError('cannot normalize vector %s' % str(self))
        return Vector(elem / norm for elem in self)

    def getDistance(self, *args):
        """Get distance from C{self} to a Vector, to an axis (two arguments),
        or signed distance to a triangle (three arguments).
        Raises ZeroDivisionError if the axis points coincide or if triangle
        is degenerate.

        >>> Vector(1,2,3).getDistance(Vector(4,-5,6)) # doctest: +ELLIPSIS
        8.185...
        >>> Vector(0,3.5,0).getDistance(Vector(0,0,0), Vector(0,0,1))
        3.5
        >>> Vector(0,1,0.5).getDistance(Vector(0,0,0), Vector(1,1,1)) # doctest: +ELLIPSIS
        0.70710678...
        >>> Vector(0,0,1).getDistance(Vector(0,0,0),Vector(1,0,0),Vector(0,1,0))
        1.0
        >>> Vector(0,0,1).getDistance(Vector(0,0,0),Vector(0,1,0),Vector(1,0,0))
        -1.0
        """

        if len(args) == 1:
            return (self - args[0]).getNorm()
        elif len(args) == 2:
            return ( self.getNormal(*args).getNorm()
                     / args[0].getDistance(args[1]) )
        elif len(args) == 3:
            normal = args[0].getNormal(args[1], args[2])
            return (normal * (self - args[0])) / normal.getNorm()

class Quat(tuple):
    """Quaternion implementation."""
    def __new__(cls, *args):
        """Quaternion constructor. Takes either a single list/tuple/generator
        argument, or multiple int, long, float arguments.

        >>> Quat(0,0,0,1)
        (0, 0, 0, 1)
        >>> Quat("abcd") # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        """
        if len(args) == 1 and isinstance(args[0], (list, tuple, GeneratorType)):
            # single list/tuple/generator type
            quat = tuple.__new__(cls, args[0])
        else:
            quat = tuple.__new__(cls, (elem for elem in args))
        if len(quat) != 4:
            raise TypeError("Quaternion must consist of exactly 4 scalars.")
        for elem in quat:
            if not isinstance(elem, (int, long, float)):
                raise TypeError("Vector must consist of scalars.")
        return quat

    def getLMatrix(self):
        """Get matrix representation."""
        raise NotImplementedError

class Matrix(tuple):
    """A general purpose matrix base class, without vector multiplication.
    For matrices that support vector multiplication, use LMatrix, RMatrix, or
    LRMatrix."""
    # note: all multiplication code (L/R)Matrix * something is implemented in
    # __mul__
    
    def __new__(cls, *args, **kwargs):
        """Initialize matrix from row vectors.

        >>> Matrix((1,2,3),(4,5,6),(7,8,9))
        ((1, 2, 3), (4, 5, 6), (7, 8, 9))
        >>> Matrix(( row for row in xrange(i, i + 3) ) for i in xrange(3))
        ((0, 1, 2), (1, 2, 3), (2, 3, 4))
        """
        if len(args) == 1 and isinstance(args[0], (list, tuple, GeneratorType)):
            # single list/tuple/generator type
            mat = tuple.__new__(cls, ( tuple(row) for row in args[0] ))
        else:
            mat = tuple.__new__(cls, ( tuple( elem for elem in row )
                                       for row in args ))
        return mat

    def __init__(self, *args, **kwargs):
        self._dim_n = len(self)
        self._dim_m = len(self[0]) if self._dim_n else 0
        for row in self:
            if len(row) != self._dim_m:
                raise ValueError("all rows must have the same length")
        for row in self:
            for elem in row:
                if not isinstance(elem, (int, long, float)):
                    raise TypeError("Matrix must consist of scalars.")

    def __str__(self):
        """Format the matrix in a string."""
        result = ""
        for row in self:
            result += "[ "
            result += ("%6s " * len(row)) % tuple(row)
            result += "]\n"
        return result

    def __add__(self, other):
        """Matrix and scalar addition.

        >>> Matrix((1,2,3),(2,3,4),(4,5,6)) + Matrix((3,2,1),(2,1,0),(1,2,3))
        ((4, 4, 4), (4, 4, 4), (5, 7, 9))
        >>> Matrix((1,2,3),(2,3,4)) + 5
        ((6, 7, 8), (7, 8, 9))
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
        ((6, 7, 8), (7, 8, 9), (9, 10, 11))
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
        ((-2, 0, 2), (0, 2, 4), (3, 3, 3))
        >>> Matrix((1,2,3),(2,3,4)) - 5
        ((-4, -3, -2), (-3, -2, -1))
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
        ((4, 3, 2), (3, 2, 1), (1, 0, -1))
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
        ((17, 23, 29), (24, 33, 42), (38, 53, 68))
        >>> Matrix((1,2,3),(2,3,4),(4,5,6)) * Vector(4,-5,6) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        >>> LMatrix((1,2,3),(2,3,4),(4,5,6)) * Vector(4,-5,6) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
        >>> Matrix((1,2,3),(2,3,4),(4,5,6)) * 5
        ((5, 10, 15), (10, 15, 20), (20, 25, 30))"""
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
        ((5, 10, 15), (10, 15, 20), (20, 25, 30))
        """
        if isinstance(other, (int, long, float)):
            return (self * other)
        else:
            raise TypeError("cannot multiply %s and %s"
                            % (other.__class__, self.__class__))

    def __eq__(self, other):
        """Compare matrices.

        >>> Matrix((1,2,3), (4,5,6)) == Matrix((1.0,2.0,3.0), (4,5,6))
        True
        >>> Matrix((1,2,3), (4,5,6)) == Matrix((1.0,2.1,3.0), (4,5,6))
        False
        """
        if isinstance(other, Matrix):
            # dimension check
            if self._dim_n != other._dim_n or self._dim_m != other._dim_m:
                raise ValueError(
                    "cannot compare matrices with different dimensions")
            for row1, row2 in izip(self, other):
                for elem1, elem2 in izip(row1, row2):
                    if abs(elem1 - elem2) > EPSILON:
                        return False
        else:
            raise TypeError(
                "do not know how to compare %s and %s"
                % (self.__class__, other.__class__))
        return True

    def __ne__(self, other):
        """Compare matrices."""
        return not self.__eq__(other)

    def setIdentity(self):
        """Set to identity matrix."""
        for i in xrange(self._dim_n):
            for j in xrange(self._dim_m):
                self[i][j] = 1 if i == j else 0

    def isIdentity(self):
        """Check if matrix is identity matrix."""
        for i in xrange(self._dim_n):
            for j in xrange(self._dim_m):
                if abs(self[i][j] - (1 if i == j else 0)) > EPSILON:
                    return False
        return True

    def getTranspose(self):
        """Get transpose of self.

        >>> Matrix((1,2,3),(2,3,4),(4,5,6)).getTranspose()
        ((1, 2, 4), (2, 3, 5), (3, 4, 6))
        >>> Matrix((1, 2), (3, 4)).getTranspose()
        ((1, 3), (2, 4))
        """
        # get type of result
        if isinstance(self, LMatrix):
            cls = RMatrix
        elif isinstance(self, RMatrix):
            cls = LMatrix
        else:
            cls = self.__class__ # self must be Matrix or LRMatrix
        return cls(*izip(*self))

    def getSubMatrix(self, sub_n, sub_m):
        """Return a submatrix from the indices C{sub_n} and C{sub_m}."""
        return self.__class__( ( self[i][j] for j in sub_m )
                               for i in sub_n )

    def getCofactor(self, i, j):
        """Return the cofactor of the (i, j) entry of the matrix."""
        return Matrix( ( self[ii][jj]
                         for jj in xrange(self._dim_m)
                         if jj != j )
                       for ii in xrange(self._dim_n)
                       if ii != i ).getDeterminant()

    def getDeterminant(self):
        """Calculate determinant.

        >>> Matrix((1,2,3), (4,5,6), (7,8,9)).getDeterminant()
        0
        >>> Matrix((1,2,4), (3,0,2), (-3,6,2)).getDeterminant()
        36
        """
        if self._dim_n != self._dim_m:
            raise ValueError(
                "cannot calculate determinant of non-square matrix")
        if self._dim_n == 0:
            return 0
        elif self._dim_n == 1:
            return self[0][0]
        elif self._dim_n == 2:
            return self[0][0] * self[1][1] - self[1][0] * self[0][1]
        else:
            return sum( (-1 if i&1 else 1) * self[i][0] * self.getCofactor(i, 0)
                        for i in xrange(self._dim_n) )

    def getInverse(self):
        """Calculate the inverse of the matrix."""

class LMatrix(Matrix):
    """A general purpose matrix class, with left vector multiplication. Use
    for linear and affine transforms."""
    # the left multiplication is implemented in the Vector class

    def __init__(self, *args, **kwargs):
        """Initialize matrix from row vectors.

        @param affine: Set C{affine = True} if the last row of the matrix
            is the translation component of the transform.
        @param args: The rows.

        >>> LMatrix((0.5,0.5,0), (0.5,-0.5,0), (7,8,1), affine = True)
        ((0.5, 0.5, 0), (0.5, -0.5, 0), (7, 8, 1))
        >>> LMatrix(( row for row in xrange(i, i + 3) ) for i in xrange(3))
        ((0, 1, 2), (1, 2, 3), (2, 3, 4))
        """
        Matrix.__init__(self, *args)
        self._affine = bool(kwargs.get("affine", False))

    def getScaleRotation(self, conformal = False):
        """Gets the scale and rotation part of the transformation. Raises
        C{ValueError} if the decomposition does not exist.

        @param conformal: If C{True} then checks for conformality (uniform
            scaling).
        @return: A Vector containing the scaling in each direction, a
            rotation matrix, and a translation Vector.

        >>> LMatrix((0,-1,0),(2,0,0),(0,0,5)).getScaleRotation()
        ((1.0, 2.0, 5.0), ((0.0, -1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)))
        """
        if self._dim_n != self._dim_m:
            raise ValueError("cannot calculate scale, rotation, and \
translation of a non-square matrix")

        # calculate self * self^T
        # this should correspond to
        # (scale * rotation) * (scale * rotation)^T
        # = scale * scale^T
        # = diagonal matrix with scales squared on the diagonal
        if self._affine:
            dim = self._dim_n - 1
            rot = self.getSubMatrix(range(dim),
                                    range(dim))
        else:
            dim = self._dim_n
            rot = self
        mat = rot * rot.getTranspose()

        # off diagonal elements should be zero
        for i in xrange(dim):
            for j in xrange(dim):
                # admit a rather large tolerance because
                # some programs do not produce nice rotation matrices
                if i != j and abs(mat[i][j]) > 0.01:
                    raise valueError("matrix does not decompose in \
non-uniform scale * rotation")

        scale = Vector(mat[i][i] ** 0.5 for i in xrange(dim))

        if conformal:
            if max(abs(scale[0] - scale[i])
                   for i in xrange(1, dim)) > EPSILON:
                raise ValueError("matrix does not decompose in \
uniform scale * rotation")

        if rot.getDeterminant() < 0:
            scale = -scale

        return scale, LMatrix( ( rot[i][j] / scale[i]
                                 for j in xrange(dim) )
                               for i in xrange(dim) )

    @classmethod
    def composeScaleRotation(cls, scale, rotation):
        """Compose scale * rotation.

        >>> x = LMatrix.composeScaleRotation(Vector(1.0, 2.0, 5.0), LMatrix((0.0, -1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)))
        >>> x
        ((0.0, -1.0, 0.0), (2.0, 0.0, 0.0), (0.0, 0.0, 5.0))
        """
        if not isinstance(scale, Vector):
            raise TypeError("first argument must be Vector")
        if not isinstance(rotation, LMatrix):
            raise TypeError("second argument must be LMatrix")
        dim = rotation._dim_n
        if rotation._dim_n != rotation._dim_m or rotation._affine:
            raise ValueError("second argument must be a %ix%i rotation matrix"
                             % (dim, dim))
        if len(scale) != dim:
            raise ValueError(
                "scale Vector must have same dimension as rotation matrix")
        if rotation.getScaleRotation()[1] != rotation:
            raise ValueError("second argument must be a rotation matrix")
        return LMatrix( ( scale[i] * rotation[i][j]
                          for j in xrange(dim) )
                        for i in xrange(dim) )

    @classmethod
    def composeScaleRotationTranslation(cls, scale, rotation, translation):
        """Compose scale * rotation * translation.

        >>> x = LMatrix.composeScaleRotationTranslation(Vector(1.0, 2.0, 5.0), LMatrix((0.0, -1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)), Vector(1, 2, 3))
        >>> x
        ((0.0, -1.0, 0.0, 0), (2.0, 0.0, 0.0, 0), (0.0, 0.0, 5.0, 0), (1, 2, 3, 1))
        """
        if not isinstance(scale, Vector):
            raise TypeError("first argument must be Vector")
        if not isinstance(rotation, LMatrix):
            raise TypeError("second argument must be LMatrix")
        if not isinstance(translation, Vector):
            raise TypeError("third argument must be Vector")
        dim = rotation._dim_n
        if rotation._dim_n != rotation._dim_m or rotation._affine:
            raise ValueError("second argument must be a %ix%i rotation matrix"
                             % (dim, dim))
        if len(scale) != dim:
            raise ValueError(
                "scale Vector must have same dimension as rotation matrix")
        if len(translation) != dim:
            raise ValueError(
                "translation Vector must have same dimension as rotation matrix")
        if rotation.getScaleRotation()[1] != rotation:
            raise ValueError("second argument must be a rotation matrix")
        return LMatrix( [ [ scale[i] * rotation[i][j]
                            for j in xrange(dim) ] + [ 0 ]
                          for i in xrange(dim) ]
                        + [ [ translation[i] for i in xrange(dim) ] + [ 1 ] ],
                        affine = True )

    def getScaleQuat(self):
        """Decompose upper 3x3 part of matrix into scale and quaternion.

        >>> LMatrix((1,0,0),(0,2,0),(0,0,5)).getScaleQuat()
        ((1.0, 2.0, 5.0), (0.0, 0.0, 0.0, 1.0))
        >>> LMatrix((0,-1,0),(2,0,0),(0,0,5)).getScaleQuat() # doctest: +ELLIPSIS
        ((1.0, 2.0, 5.0), (0.0, 0.0, -0.7071..., 0.7071...))
        """
        scale, rot = self.getScaleRotation()
        if len(scale) != 3:
            raise ValueError("matrix must be 3x3 (linear) or 4x4 (affine)")

        trace = sum((rot[i][i] for i in xrange(3)), 1.0)
        
        if trace > EPSILON:
            s = (trace ** 0.5) * 2
            return scale, Quat( ( rot[1][2] - rot[2][1] ) / s,
                                ( rot[2][0] - rot[0][2] ) / s,
                                ( rot[0][1] - rot[1][0] ) / s,
                                0.25 * s )
        elif rot[0][0] > max((rot[1][1], rot[2][2])): 
            s  = (( 1.0 + rot[0][0] - rot[1][1] - rot[2][2] ) ** 0.5) * 2
            return scale, Quat( 0.25 * s,
                                ( rot[0][1] + rot[1][0] ) / s,
                                ( rot[2][0] + rot[0][2] ) / s,
                                ( rot[1][2] - rot[2][1] ) / s )
        elif rot[1][1] > rot[2][2]:
            s  = (( 1.0 + rot[1][1] - rot[0][0] - rot[2][2] ) ** 0.5) * 2
            return scale, Quat( ( rot[0][1] + rot[1][0] ) / s,
                                0.25 * s,
                                ( rot[1][2] + rot[2][1] ) / s,
                                ( rot[2][0] - rot[0][2] ) / s )
        else:
            s  = (( 1.0 + rot[2][2] - rot[0][0] - rot[1][1] ) ** 0.5) * 2
            return scale, Quat( ( rot[2][0] + rot[0][2] ) / s,
                                ( rot[1][2] + rot[2][1] ) / s,
                                0.25 * s,
                                ( rot[0][1] - rot[1][0] ) / s )

        return scale, quat

    def getTranslation(self):
        """Returns translation part (zero Vector for non-affine transforms).

        >>> x = LMatrix((0.5,-0.5,0),(0.5,0.5,0),(7,8,1), affine = True)
        >>> x.getTranslation()
        (7, 8)
        """
        if self._affine:
            return Vector(self[-1][j] for j in xrange(self._dim_m - 1))
        else:
            return Vector(0 for j in xrange(self._dim_m - 1))

    def getScaled(self, scale):
        """Return matrix with translation component scaled."""
        if not self._affine:
            raise ValueError("getScaled only makes sense for affine transforms.")
        return LMatrix( self[:-1]
                        +
                        ( tuple( elem * scale
                                 for elem in self[-1][:-1] )
                          + ( self[-1][-1], ), ),
                        affine = True )

class RMatrix(Matrix):
    """A general purpose matrix class, with vector multiplication from the
    right. Use for linear transforms."""
    # the right multiplication is implemented in the Matrix class



class LRMatrix(Matrix):
    """A general purpose matrix class, with vector multiplication from both
    sides. Use for bilinear forms (such as inertia tensors)."""
    
    def innerProduct(self, vec1, vec2):
        """Inner product of two vectors."""
        return sum( sum( vec1[i] * self[i][j]
                         for i in xrange(self._dim_n) )
                    * vec2[j]
                    for j in xrange(self._dim_m) )

if __name__ == "__main__":
    import doctest
    doctest.testmod()
