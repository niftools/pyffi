# --------------------------------------------------------------------------
# NifFormat.Matrix44
# Custom functions for Matrix44.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, NIF File Format Library and Tools.
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
#    * Neither the name of the NIF File Format Library and Tools
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
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

def asList(self):
    """Return matrix as 4x4 list."""
    return [
        [self.m11, self.m12, self.m13, self.m14],
        [self.m21, self.m22, self.m23, self.m24],
        [self.m31, self.m32, self.m33, self.m34],
        [self.m41, self.m42, self.m43, self.m44]
        ]

def __str__(self):
    return "[ %6.3f %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f %6.3f ]\n"%(self.m11, self.m12, self.m13, self.m14, self.m21, self.m22, self.m23, self.m24, self.m31, self.m32, self.m33, self.m34, self.m41, self.m42, self.m43, self.m44)

def setIdentity(self):
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
    if  abs(self.m11 - 1.0) > self.cls._EPSILON or abs(self.m12) > self.cls._EPSILON or abs(self.m13) > self.cls._EPSILON or abs(self.m14) > self.cls._EPSILON or abs(self.m21) > self.cls._EPSILON or abs(self.m22 - 1.0) > self.cls._EPSILON or abs(self.m23) > self.cls._EPSILON or abs(self.m24) > self.cls._EPSILON or abs(self.m31) > self.cls._EPSILON or abs(self.m32) > self.cls._EPSILON or abs(self.m33 - 1.0) > self.cls._EPSILON or abs(self.m34) > self.cls._EPSILON or abs(self.m41) > self.cls._EPSILON or abs(self.m42) > self.cls._EPSILON or abs(self.m43) > self.cls._EPSILON or abs(self.m44 - 1.0) > self.cls._EPSILON:
        return False
    else:
        return True

def getCopy(self):
    m = self.cls.Matrix44()
    m.m11 = self.m11
    m.m12 = self.m12
    m.m13 = self.m13
    m.m14 = self.m14
    m.m21 = self.m21
    m.m22 = self.m22
    m.m23 = self.m23
    m.m24 = self.m24
    m.m31 = self.m31
    m.m32 = self.m32
    m.m33 = self.m33
    m.m34 = self.m34
    m.m41 = self.m41
    m.m42 = self.m42
    m.m43 = self.m43
    m.m44 = self.m44
    return m

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

def getScaleRotationTranslation(self):
    r = self.getMatrix33()
    s = r.getScale()
    r /= s
    t = self.getTranslation()
    return (s, r, t)

def setScaleRotationTranslation(self, scale, rotation, translation):
    if not isinstance(scale, (float, int, long)):
        raise TypeError('scale must be float')
    if not isinstance(rotation, self.cls.Matrix33):
        raise TypeError('rotation must be Matrix33')
    if not isinstance(translation, self.cls.Vector3):
        raise TypeError('translation must be Vector3')

    if not rotation.isRotation():
        raise ValueError('rotation must be rotation matrix')

    self.m14 = 0.0
    self.m24 = 0.0
    self.m34 = 0.0
    self.m44 = 1.0

    self.setMatrix33(rotation * scale)
    self.setTranslation(translation)

def getInverse(self):
    """Calculates inverse; assuming scale, rotation, translation
    decomposition holds."""
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
        m.m24 = self.m21 * x
        m.m31 = self.m31 * x
        m.m32 = self.m32 * x
        m.m33 = self.m33 * x
        m.m34 = self.m34 * x
        m.m41 = self.m41 * x
        m.m42 = self.m42 * x
        m.m43 = self.m43 * x
        m.m44 = self.m44 * x
        return m
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
        raise TypeError("do not know how to multiply Matrix33 with %s"%x.__class__)

def __div__(self, x):
    if isinstance(x, (float, int, long)):
        m = self.cls.Matrix33()
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
        raise TypeError("do not know how to divide Matrix33 by %s"%x.__class__)

def __rmul__(self, x):
    if isinstance(x, (float, int, long)):
        return self * x
    else:
        raise TypeError("do not know how to multiply %s with Matrix33"%x.__class__)
