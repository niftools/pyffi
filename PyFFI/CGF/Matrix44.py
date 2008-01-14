"""Custom Matrix44 functions."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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
    """Return matrix as 4x4 list."""
    return [
        [self.m11, self.m12, self.m13, self.m14],
        [self.m21, self.m22, self.m23, self.m24],
        [self.m31, self.m32, self.m33, self.m34],
        [self.m41, self.m42, self.m43, self.m44]
        ]

def asTuple(self):
    """Return matrix as 4x4 tuple."""
    return (
        (self.m11, self.m12, self.m13, self.m14),
        (self.m21, self.m22, self.m23, self.m24),
        (self.m31, self.m32, self.m33, self.m34),
        (self.m41, self.m42, self.m43, self.m44)
        )

def setRows(self, row0, row1, row2, row3):
    """Set matrix from rows."""
    self.m11, self.m12, self.m13, self.m14 = row0
    self.m21, self.m22, self.m23, self.m24 = row1
    self.m31, self.m32, self.m33, self.m34 = row2
    self.m41, self.m42, self.m43, self.m44 = row3

def __str__(self):
    return """\
[ %6.3f %6.3f %6.3f %6.3f ]
[ %6.3f %6.3f %6.3f %6.3f ]
[ %6.3f %6.3f %6.3f %6.3f ]
[ %6.3f %6.3f %6.3f %6.3f ]
""" % (self.m11, self.m12, self.m13, self.m14,
       self.m21, self.m22, self.m23, self.m24,
       self.m31, self.m32, self.m33, self.m34,
       self.m41, self.m42, self.m43, self.m44)

def setIdentity(self):
    """Set to identity matrix."""
    self.m11 = 1.0
    self.m12 = 0.0
    self.m13 = 0.0
    self.m14 = 0.0
    self.m21 = 0.0
    self.m22 = 1.0
    self.m23 = 0.0
    self.m24 = 0.0
    self.m31 = 0.0
    self.m32 = 0.0
    self.m33 = 1.0
    self.m34 = 0.0
    self.m41 = 0.0
    self.m42 = 0.0
    self.m43 = 0.0
    self.m44 = 1.0

def isIdentity(self):
    """Return C{True} if the matrix is close to identity."""
    if (abs(self.m11 - 1.0) > self.cls.EPSILON
        or abs(self.m12) > self.cls.EPSILON
        or abs(self.m13) > self.cls.EPSILON
        or abs(self.m14) > self.cls.EPSILON
        or abs(self.m21) > self.cls.EPSILON
        or abs(self.m22 - 1.0) > self.cls.EPSILON
        or abs(self.m23) > self.cls.EPSILON
        or abs(self.m24) > self.cls.EPSILON
        or abs(self.m31) > self.cls.EPSILON
        or abs(self.m32) > self.cls.EPSILON
        or abs(self.m33 - 1.0) > self.cls.EPSILON
        or abs(self.m34) > self.cls.EPSILON
        or abs(self.m41) > self.cls.EPSILON
        or abs(self.m42) > self.cls.EPSILON
        or abs(self.m43) > self.cls.EPSILON
        or abs(self.m44 - 1.0) > self.cls.EPSILON):
        return False
    else:
        return True

def getCopy(self):
    """Create a copy of the matrix."""
    mat = self.cls.Matrix44()
    mat.m11 = self.m11
    mat.m12 = self.m12
    mat.m13 = self.m13
    mat.m14 = self.m14
    mat.m21 = self.m21
    mat.m22 = self.m22
    mat.m23 = self.m23
    mat.m24 = self.m24
    mat.m31 = self.m31
    mat.m32 = self.m32
    mat.m33 = self.m33
    mat.m34 = self.m34
    mat.m41 = self.m41
    mat.m42 = self.m42
    mat.m43 = self.m43
    mat.m44 = self.m44
    return mat

def getMatrix33(self):
    """Returns upper left 3x3 part."""
    m = self.cls.Matrix33()
    m.m11 = self.m11
    m.m12 = self.m12
    m.m13 = self.m13
    m.m21 = self.m21
    m.m22 = self.m22
    m.m23 = self.m23
    m.m31 = self.m31
    m.m32 = self.m32
    m.m33 = self.m33
    return m

def setMatrix33(self, m):
    """Sets upper left 3x3 part."""
    if not isinstance(m, self.cls.Matrix33):
        raise TypeError('argument must be Matrix33')
    self.m11 = m.m11
    self.m12 = m.m12
    self.m13 = m.m13
    self.m21 = m.m21
    self.m22 = m.m22
    self.m23 = m.m23
    self.m31 = m.m31
    self.m32 = m.m32
    self.m33 = m.m33

def getTranslation(self):
    """Returns lower left 1x3 part."""
    t = self.cls.Vector3()
    t.x = self.m41
    t.y = self.m42
    t.z = self.m43
    return t

def setTranslation(self, translation):
    """Returns lower left 1x3 part."""
    if not isinstance(translation, self.cls.Vector3):
        raise TypeError('argument must be Vector3')
    self.m41 = translation.x
    self.m42 = translation.y
    self.m43 = translation.z

def isScaleRotationTranslation(self):
    if not self.getMatrix33().isScaleRotation(): return False
    if abs(self.m14) > self.cls.EPSILON: return False
    if abs(self.m24) > self.cls.EPSILON: return False
    if abs(self.m34) > self.cls.EPSILON: return False
    if abs(self.m44 - 1.0) > self.cls.EPSILON: return False
    return True

def getScaleRotationTranslation(self):
    rotscl = self.getMatrix33()
    scale, rot = rotscl.getScaleRotation()
    trans = self.getTranslation()
    return (scale, rot, trans)

def getScaleQuatTranslation(self):
    rotscl = self.getMatrix33()
    scale, quat = rotscl.getScaleQuat()
    trans = self.getTranslation()
    return (scale, quat, trans)

def setScaleRotationTranslation(self, scale, rotation, translation):
    if not isinstance(scale, self.cls.Vector3):
        raise TypeError('scale must be Vector3')
    if not isinstance(rotation, self.cls.Matrix33):
        raise TypeError('rotation must be Matrix33')
    if not isinstance(translation, self.cls.Vector3):
        raise TypeError('translation must be Vector3')

    if not rotation.isRotation():
        print "WARNING (setScaleRotationTranslation): improper rotation matrix"
        print rotation
        #raise ValueError('rotation must be rotation matrix')

    self.m14 = 0.0
    self.m24 = 0.0
    self.m34 = 0.0
    self.m44 = 1.0

    rotscl = rotation.getCopy()
    rotscl.m11 *= scale.x
    rotscl.m12 *= scale.x
    rotscl.m13 *= scale.x
    rotscl.m21 *= scale.y
    rotscl.m22 *= scale.y
    rotscl.m23 *= scale.y
    rotscl.m31 *= scale.z
    rotscl.m32 *= scale.z
    rotscl.m33 *= scale.z

    self.setMatrix33(rotscl)
    self.setTranslation(translation)

def getInverse(self, fast = True):
    """Calculates inverse (fast assumes isScaleRotationTranslation is True)."""
    def adjoint(m, ii, jj):
        result = []
        for i, row in enumerate(m):
            if i == ii: continue
            result.append([])
            for j, x in enumerate(row):
                if j == jj: continue
                result[-1].append(x)
        return result
    def determinant(m):
        if len(m) == 2:
            return m[0][0]*m[1][1] - m[1][0]*m[0][1]
        result = 0.0
        for i in xrange(len(m)):
            det = determinant(adjoint(m, i, 0))
            if i & 1:
                result -= m[i][0] * det
            else:
                result += m[i][0] * det
        return result

    if fast:
        m = self.getMatrix33().getInverse()
        t = -(self.getTranslation() * m)

        n = self.cls.Matrix44()
        n.m14 = 0.0
        n.m24 = 0.0
        n.m34 = 0.0
        n.m44 = 1.0
        n.setMatrix33(m)
        n.setTranslation(t)
        return n
    else:
        m = self.asList()
        nn = [[0.0 for i in xrange(4)] for j in xrange(4)]
        det = determinant(m)
        if abs(det) < self.cls.EPSILON:
            raise ZeroDivisionError('cannot invert matrix:\n%s'%self)
        for i in xrange(4):
            for j in xrange(4):
                if (i+j) & 1:
                    nn[j][i] = -determinant(adjoint(m, i, j)) / det
                else:
                    nn[j][i] = determinant(adjoint(m, i, j)) / det
        n = self.cls.Matrix44()
        n.setRows(*nn)
        return n

def __mul__(self, x):
    if isinstance(x, (float, int, long)):
        m = self.cls.Matrix44()
        m.m11 = self.m11 * x
        m.m12 = self.m12 * x
        m.m13 = self.m13 * x
        m.m14 = self.m14 * x
        m.m21 = self.m21 * x
        m.m22 = self.m22 * x
        m.m23 = self.m23 * x
        m.m24 = self.m24 * x
        m.m31 = self.m31 * x
        m.m32 = self.m32 * x
        m.m33 = self.m33 * x
        m.m34 = self.m34 * x
        m.m41 = self.m41 * x
        m.m42 = self.m42 * x
        m.m43 = self.m43 * x
        m.m44 = self.m44 * x
        return m
    elif isinstance(x, self.cls.Vector3):
        raise TypeError("matrix*vector not supported; please use left multiplication (vector*matrix)")
    elif isinstance(x, self.cls.Vector4):
        raise TypeError("matrix*vector not supported; please use left multiplication (vector*matrix)")
    elif isinstance(x, self.cls.Matrix44):
        m = self.cls.Matrix44()
        m.m11 = self.m11 * x.m11  +  self.m12 * x.m21  +  self.m13 * x.m31  +  self.m14 * x.m41
        m.m12 = self.m11 * x.m12  +  self.m12 * x.m22  +  self.m13 * x.m32  +  self.m14 * x.m42
        m.m13 = self.m11 * x.m13  +  self.m12 * x.m23  +  self.m13 * x.m33  +  self.m14 * x.m43
        m.m14 = self.m11 * x.m14  +  self.m12 * x.m24  +  self.m13 * x.m34  +  self.m14 * x.m44
        m.m21 = self.m21 * x.m11  +  self.m22 * x.m21  +  self.m23 * x.m31  +  self.m24 * x.m41
        m.m22 = self.m21 * x.m12  +  self.m22 * x.m22  +  self.m23 * x.m32  +  self.m24 * x.m42
        m.m23 = self.m21 * x.m13  +  self.m22 * x.m23  +  self.m23 * x.m33  +  self.m24 * x.m43
        m.m24 = self.m21 * x.m14  +  self.m22 * x.m24  +  self.m23 * x.m34  +  self.m24 * x.m44
        m.m31 = self.m31 * x.m11  +  self.m32 * x.m21  +  self.m33 * x.m31  +  self.m34 * x.m41
        m.m32 = self.m31 * x.m12  +  self.m32 * x.m22  +  self.m33 * x.m32  +  self.m34 * x.m42
        m.m33 = self.m31 * x.m13  +  self.m32 * x.m23  +  self.m33 * x.m33  +  self.m34 * x.m43
        m.m34 = self.m31 * x.m14  +  self.m32 * x.m24  +  self.m33 * x.m34  +  self.m34 * x.m44
        m.m41 = self.m41 * x.m11  +  self.m42 * x.m21  +  self.m43 * x.m31  +  self.m44 * x.m41
        m.m42 = self.m41 * x.m12  +  self.m42 * x.m22  +  self.m43 * x.m32  +  self.m44 * x.m42
        m.m43 = self.m41 * x.m13  +  self.m42 * x.m23  +  self.m43 * x.m33  +  self.m44 * x.m43
        m.m44 = self.m41 * x.m14  +  self.m42 * x.m24  +  self.m43 * x.m34  +  self.m44 * x.m44
        return m
    else:
        raise TypeError("do not know how to multiply Matrix44 with %s"%x.__class__)

def __div__(self, x):
    if isinstance(x, (float, int, long)):
        m = self.cls.Matrix44()
        m.m11 = self.m11 / x
        m.m12 = self.m12 / x
        m.m13 = self.m13 / x
        m.m14 = self.m14 / x
        m.m21 = self.m21 / x
        m.m22 = self.m22 / x
        m.m23 = self.m23 / x
        m.m24 = self.m24 / x
        m.m31 = self.m31 / x
        m.m32 = self.m32 / x
        m.m33 = self.m33 / x
        m.m34 = self.m34 / x
        m.m41 = self.m41 / x
        m.m42 = self.m42 / x
        m.m43 = self.m43 / x
        m.m44 = self.m44 / x
        return m
    else:
        raise TypeError("do not know how to divide Matrix44 by %s"%x.__class__)

def __rmul__(self, x):
    if isinstance(x, (float, int, long)):
        return self * x
    else:
        raise TypeError("do not know how to multiply %s with Matrix44"%x.__class__)

def __eq__(self, m):
    if isinstance(m, NoneType):
        return False
    if not isinstance(m, self.cls.Matrix44):
        raise TypeError("do not know how to compare Matrix44 and %s"%m.__class__)
    if abs(self.m11 - m.m11) > self.cls.EPSILON: return False
    if abs(self.m12 - m.m12) > self.cls.EPSILON: return False
    if abs(self.m13 - m.m13) > self.cls.EPSILON: return False
    if abs(self.m14 - m.m14) > self.cls.EPSILON: return False
    if abs(self.m21 - m.m21) > self.cls.EPSILON: return False
    if abs(self.m22 - m.m22) > self.cls.EPSILON: return False
    if abs(self.m23 - m.m23) > self.cls.EPSILON: return False
    if abs(self.m24 - m.m24) > self.cls.EPSILON: return False
    if abs(self.m31 - m.m31) > self.cls.EPSILON: return False
    if abs(self.m32 - m.m32) > self.cls.EPSILON: return False
    if abs(self.m33 - m.m33) > self.cls.EPSILON: return False
    if abs(self.m34 - m.m34) > self.cls.EPSILON: return False
    if abs(self.m41 - m.m41) > self.cls.EPSILON: return False
    if abs(self.m42 - m.m42) > self.cls.EPSILON: return False
    if abs(self.m43 - m.m43) > self.cls.EPSILON: return False
    if abs(self.m44 - m.m44) > self.cls.EPSILON: return False
    return True

def __ne__(self, m):
    return not self.__eq__(m)

def __add__(self, x):
    if isinstance(x, (self.cls.Matrix44)):
        m = self.cls.Matrix44()
        m.m11 = self.m11 + x.m11
        m.m12 = self.m12 + x.m12
        m.m13 = self.m13 + x.m13
        m.m14 = self.m14 + x.m14
        m.m21 = self.m21 + x.m21
        m.m22 = self.m22 + x.m22
        m.m23 = self.m23 + x.m23
        m.m24 = self.m24 + x.m24
        m.m31 = self.m31 + x.m31
        m.m32 = self.m32 + x.m32
        m.m33 = self.m33 + x.m33
        m.m34 = self.m34 + x.m34
        m.m41 = self.m41 + x.m41
        m.m42 = self.m42 + x.m42
        m.m43 = self.m43 + x.m43
        m.m44 = self.m44 + x.m44
        return m
    elif isinstance(x, (int, long, float)):
        m = self.cls.Matrix44()
        m.m11 = self.m11 + x
        m.m12 = self.m12 + x
        m.m13 = self.m13 + x
        m.m14 = self.m14 + x
        m.m21 = self.m21 + x
        m.m22 = self.m22 + x
        m.m23 = self.m23 + x
        m.m24 = self.m24 + x
        m.m31 = self.m31 + x
        m.m32 = self.m32 + x
        m.m33 = self.m33 + x
        m.m34 = self.m34 + x
        m.m41 = self.m41 + x
        m.m42 = self.m42 + x
        m.m43 = self.m43 + x
        m.m44 = self.m44 + x
        return m
    else:
        raise TypeError("do not know how to add Matrix44 and %s"%x.__class__)

