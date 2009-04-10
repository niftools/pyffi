"""Custom Matrix33 functions."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
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

def asList(self):
    """Return matrix as 3x3 list."""
    return [
        [self.m11, self.m12, self.m13],
        [self.m21, self.m22, self.m23],
        [self.m31, self.m32, self.m33]
        ]

def asTuple(self):
    """Return matrix as 3x3 tuple."""
    return (
        (self.m11, self.m12, self.m13),
        (self.m21, self.m22, self.m23),
        (self.m31, self.m32, self.m33)
        )

def __str__(self):
    return "\
[ %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f ]\n"\
% (self.m11, self.m12, self.m13,
   self.m21, self.m22, self.m23,
   self.m31, self.m32, self.m33)

def setIdentity(self):
    """Set to identity matrix."""
    self.m11 = 1.0
    self.m12 = 0.0
    self.m13 = 0.0
    self.m21 = 0.0
    self.m22 = 1.0
    self.m23 = 0.0
    self.m31 = 0.0
    self.m32 = 0.0
    self.m33 = 1.0

def isIdentity(self):
    """Return C{True} if the matrix is close to identity."""
    if  (abs(self.m11 - 1.0) > self.cls.EPSILON
         or abs(self.m12) > self.cls.EPSILON
         or abs(self.m13) > self.cls.EPSILON
         or abs(self.m21) > self.cls.EPSILON
         or abs(self.m22 - 1.0) > self.cls.EPSILON
         or abs(self.m23) > self.cls.EPSILON
         or abs(self.m31) > self.cls.EPSILON
         or abs(self.m32) > self.cls.EPSILON
         or abs(self.m33 - 1.0) > self.cls.EPSILON):
        return False
    else:
        return True

def getCopy(self):
    """Return a copy of the matrix."""
    mat = self.cls.Matrix33()
    mat.m11 = self.m11
    mat.m12 = self.m12
    mat.m13 = self.m13
    mat.m21 = self.m21
    mat.m22 = self.m22
    mat.m23 = self.m23
    mat.m31 = self.m31
    mat.m32 = self.m32
    mat.m33 = self.m33
    return mat

def getTranspose(self):
    """Get transposed of the matrix."""
    mat = self.cls.Matrix33()
    mat.m11 = self.m11
    mat.m12 = self.m21
    mat.m13 = self.m31
    mat.m21 = self.m12
    mat.m22 = self.m22
    mat.m23 = self.m32
    mat.m31 = self.m13
    mat.m32 = self.m23
    mat.m33 = self.m33
    return mat

def isScaleRotation(self):
    """Returns true if the matrix decomposes nicely into scale * rotation."""
    # NOTE: 0.01 instead of self.cls.EPSILON to work around bad nif files

    # calculate self * self^T
    # this should correspond to
    # (scale * rotation) * (scale * rotation)^T
    # = scale * rotation * rotation^T * scale^T
    # = scale * scale^T
    self_transpose = self.getTranspose()
    mat = self * self_transpose

    # off diagonal elements should be zero
    if (abs(mat.m12) + abs(mat.m13)
        + abs(mat.m21) + abs(mat.m23)
        + abs(mat.m31) + abs(mat.m32)) > 0.01:
        return False

    return True

def isRotation(self):
    """Returns C{True} if the matrix is a rotation matrix
    (a member of SO(3))."""
    # NOTE: 0.01 instead of self.cls.EPSILON to work around bad nif files

    if not self.isScaleRotation():
        return False
    scale = self.getScale()
    if abs(scale.x - 1.0) > 0.01 \
       or abs(scale.y - 1.0) > 0.01 \
       or abs(scale.z - 1.0) > 0.01:
        return False
    return True

def getDeterminant(self):
    """Return determinant."""
    return (self.m11*self.m22*self.m33
            +self.m12*self.m23*self.m31
            +self.m13*self.m21*self.m32
            -self.m31*self.m22*self.m13
            -self.m21*self.m12*self.m33
            -self.m11*self.m32*self.m23)

def getScale(self):
    """Gets the scale (assuming isScaleRotation is true!)."""
    # calculate self * self^T
    # this should correspond to
    # (rotation * scale)* (rotation * scale)^T
    # = scale * scale^T
    # = diagonal matrix with scales squared on the diagonal
    mat = self * self.getTranspose()

    scale = self.cls.Vector3()
    scale.x = mat.m11 ** 0.5
    scale.y = mat.m22 ** 0.5
    scale.z = mat.m33 ** 0.5

    if self.getDeterminant() < 0:
        return -scale
    else:
        return scale

def getScaleRotation(self):
    """Decompose the matrix into scale and rotation, where scale is a float
    and rotation is a C{Matrix33}. Returns a pair (scale, rotation)."""
    rot = self.getCopy()
    scale = self.getScale()
    if min(abs(x) for x in scale.asTuple()) < self.cls.EPSILON:
        raise ZeroDivisionError('scale is zero, unable to obtain rotation')
    rot.m11 /= scale.x
    rot.m12 /= scale.x
    rot.m13 /= scale.x
    rot.m21 /= scale.y
    rot.m22 /= scale.y
    rot.m23 /= scale.y
    rot.m31 /= scale.z
    rot.m32 /= scale.z
    rot.m33 /= scale.z
    return (scale, rot)

def setScaleRotation(self, scale, rotation):
    """Compose the matrix as the product of scale * rotation."""
    if not isinstance(scale, self.cls.Vector3):
        raise TypeError('scale must be Vector3')
    if not isinstance(rotation, self.cls.Matrix33):
        raise TypeError('rotation must be Matrix33')

    if not rotation.isRotation():
        raise ValueError('rotation must be rotation matrix')

    self.m11 = rotation.m11 * scale.x
    self.m12 = rotation.m12 * scale.x
    self.m13 = rotation.m13 * scale.x
    self.m21 = rotation.m21 * scale.y
    self.m22 = rotation.m22 * scale.y
    self.m23 = rotation.m23 * scale.y
    self.m31 = rotation.m31 * scale.z
    self.m32 = rotation.m32 * scale.z
    self.m33 = rotation.m33 * scale.z

def getScaleQuat(self):
    """Decompose matrix into scale and quaternion."""
    scale, rot = self.getScaleRotation()
    quat = self.cls.Quat()
    trace = 1.0 + rot.m11 + rot.m22 + rot.m33

    if trace > self.cls.EPSILON:
        s = (trace ** 0.5) * 2
        quat.x = -( rot.m32 - rot.m23 ) / s
        quat.y = -( rot.m13 - rot.m31 ) / s
        quat.z = -( rot.m21 - rot.m12 ) / s
        quat.w = 0.25 * s
    elif rot.m11 > max((rot.m22, rot.m33)):
        s  = (( 1.0 + rot.m11 - rot.m22 - rot.m33 ) ** 0.5) * 2
        quat.x = 0.25 * s
        quat.y = (rot.m21 + rot.m12 ) / s
        quat.z = (rot.m13 + rot.m31 ) / s
        quat.w = -(rot.m32 - rot.m23 ) / s
    elif rot.m22 > rot.m33:
        s  = (( 1.0 + rot.m22 - rot.m11 - rot.m33 ) ** 0.5) * 2
        quat.x = (rot.m21 + rot.m12 ) / s
        quat.y = 0.25 * s
        quat.z = (rot.m32 + rot.m23 ) / s
        quat.w = -(rot.m13 - rot.m31 ) / s
    else:
        s  = (( 1.0 + rot.m33 - rot.m11 - rot.m22 ) ** 0.5) * 2
        quat.x = (rot.m13 + rot.m31 ) / s
        quat.y = (rot.m32 + rot.m23 ) / s
        quat.z = 0.25 * s
        quat.w = -(rot.m21 - rot.m12 ) / s

    return scale, quat


def getInverse(self):
    """Get inverse (assuming isScaleRotation is true!)."""
    # transpose inverts rotation but keeps the scale
    # dividing by scale^2 inverts the scale as well
    scale = self.getScale()
    mat = self.getTranspose()
    mat.m11 /= scale.x ** 2
    mat.m12 /= scale.x ** 2
    mat.m13 /= scale.x ** 2
    mat.m21 /= scale.y ** 2
    mat.m22 /= scale.y ** 2
    mat.m23 /= scale.y ** 2
    mat.m31 /= scale.z ** 2
    mat.m32 /= scale.z ** 2
    mat.m33 /= scale.z ** 2

def __mul__(self, rhs):
    if isinstance(rhs, (float, int, long)):
        mat = self.cls.Matrix33()
        mat.m11 = self.m11 * rhs
        mat.m12 = self.m12 * rhs
        mat.m13 = self.m13 * rhs
        mat.m21 = self.m21 * rhs
        mat.m22 = self.m22 * rhs
        mat.m23 = self.m23 * rhs
        mat.m31 = self.m31 * rhs
        mat.m32 = self.m32 * rhs
        mat.m33 = self.m33 * rhs
        return mat
    elif isinstance(rhs, self.cls.Vector3):
        raise TypeError("matrix*vector not supported;\
please use left multiplication (vector*matrix)")
    elif isinstance(rhs, self.cls.Matrix33):
        mat = self.cls.Matrix33()
        mat.m11 = self.m11 * rhs.m11 + self.m12 * rhs.m21 + self.m13 * rhs.m31
        mat.m12 = self.m11 * rhs.m12 + self.m12 * rhs.m22 + self.m13 * rhs.m32
        mat.m13 = self.m11 * rhs.m13 + self.m12 * rhs.m23 + self.m13 * rhs.m33
        mat.m21 = self.m21 * rhs.m11 + self.m22 * rhs.m21 + self.m23 * rhs.m31
        mat.m22 = self.m21 * rhs.m12 + self.m22 * rhs.m22 + self.m23 * rhs.m32
        mat.m23 = self.m21 * rhs.m13 + self.m22 * rhs.m23 + self.m23 * rhs.m33
        mat.m31 = self.m31 * rhs.m11 + self.m32 * rhs.m21 + self.m33 * rhs.m31
        mat.m32 = self.m31 * rhs.m12 + self.m32 * rhs.m22 + self.m33 * rhs.m32
        mat.m33 = self.m31 * rhs.m13 + self.m32 * rhs.m23 + self.m33 * rhs.m33
        return mat
    else:
        raise TypeError(
            "do not know how to multiply Matrix33 with %s"%rhs.__class__)

def __div__(self, rhs):
    if isinstance(rhs, (float, int, long)):
        mat = self.cls.Matrix33()
        mat.m11 = self.m11 / rhs
        mat.m12 = self.m12 / rhs
        mat.m13 = self.m13 / rhs
        mat.m21 = self.m21 / rhs
        mat.m22 = self.m22 / rhs
        mat.m23 = self.m23 / rhs
        mat.m31 = self.m31 / rhs
        mat.m32 = self.m32 / rhs
        mat.m33 = self.m33 / rhs
        return mat
    else:
        raise TypeError(
            "do not know how to divide Matrix33 by %s"%rhs.__class__)

def __rmul__(self, lhs):
    if isinstance(lhs, (float, int, long)):
        return self * lhs # commutes
    else:
        raise TypeError(
            "do not know how to multiply %s with Matrix33"%lhs.__class__)

def __eq__(self, mat):
    if not isinstance(mat, self.cls.Matrix33):
        raise TypeError(
            "do not know how to compare Matrix33 and %s"%mat.__class__)
    if (abs(self.m11 - mat.m11) > self.cls.EPSILON
        or abs(self.m12 - mat.m12) > self.cls.EPSILON
        or abs(self.m13 - mat.m13) > self.cls.EPSILON
        or abs(self.m21 - mat.m21) > self.cls.EPSILON
        or abs(self.m22 - mat.m22) > self.cls.EPSILON
        or abs(self.m23 - mat.m23) > self.cls.EPSILON
        or abs(self.m31 - mat.m31) > self.cls.EPSILON
        or abs(self.m32 - mat.m32) > self.cls.EPSILON
        or abs(self.m33 - mat.m33) > self.cls.EPSILON):
        return False
    return True

def __ne__(self, mat):
    return not self.__eq__(mat)
