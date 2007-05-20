# --------------------------------------------------------------------------
# NifFormat.Matrix33
# Custom functions for Matrix33.
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
    """Return matrix as 3x3 list."""
    return [
        [self.m11, self.m12, self.m13],
        [self.m21, self.m22, self.m23],
        [self.m31, self.m32, self.m33]
        ]

def __str__(self):
    return "[ %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f ]\n"%(self.m11, self.m12, self.m13, self.m21, self.m22, self.m23, self.m31, self.m32, self.m33)

def setIdentity(self):
    self.m11 = 1.0
    self.m12 = 0.0
    self.m13 = 0.0
    self.m21 = 0.0
    self.m22 = 1.0
    self.m23 = 0.0
    self.m31 = 0.0
    self.m32 = 0.0
    self.m33 = 1.0

def getCopy(self):
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

def getTranspose(self):
    """Restricts matrix to upper left 3x3 part (similar to rotationPart in Blender)."""
    m = self.cls.Matrix33()
    m.m11 = self.m11
    m.m12 = self.m21
    m.m13 = self.m31
    m.m21 = self.m12
    m.m22 = self.m22
    m.m23 = self.m32
    m.m31 = self.m13
    m.m32 = self.m23
    m.m33 = self.m33
    return m

def isScaleRotation(self):
    """Returns true if the matrix decomposes nicely into scale * rotation."""
    # calculate self * self^T
    # this should correspond to
    # (scale * rotation) * (scale * rotation)^T
    # = scale^2 * rotation * rotation^T
    # = scale^2 * 3x3 identity matrix
    selfT = self.getTranspose()
    m = self*selfT

    # off diagonal elements should be zero
    if abs(m.m12) + abs(m.m13) + abs(m.m21) + abs(m.m23) + abs(m.m31) + abs(m.m32) > self.cls._EPSILON:
        return False

    # diagonal elements should be equal (to scale^2)
    if abs(m.m11 - m.m22) + abs(m.m22 - m.m33) > self.cls._EPSILON:
        return False

    return True

def isRotation(self):
    """Returns true if the matrix is a rotation matrix."""
    if not self.isScaleRotation(): return False
    if abs(self.getScale() - 1.0) > self.cls._EPSILON: return False
    return True

def getDeterminant(self):
    return self.m11*self.m22*self.m33+self.m12*self.m23*self.m31+self.m13*self.m21*self.m32-self.m31*self.m22*self.m13-self.m21*self.m12*self.m33-self.m11*self.m32*self.m23

def getScale(self):
    s = (self.m11*self.m11 + self.m12*self.m12 + self.m13*self.m13) ** 0.5
    if self.getDeterminant() < 0: s = -s
    return s

def getScaleRotation(self):
    r = self.getCopy()
    s = self.getScale()
    if abs(s) < self.cls._EPSILON: raise ZeroDivisionError('scale is zero, unable to obtain rotation')
    r /= s
    return (s, r)

def setScaleRotation(self, scale, rotation):
    if not isinstance(scale, (float, int, long)):
        raise TypeError('scale must be float')
    if not isinstance(rotation, self.cls.Matrix33):
        raise TypeError('rotation must be Matrix33')

    if not rotation.isRotation():
        raise ValueError('rotation must be rotation matrix')

    self.m11 = rotation.m11 * scale
    self.m12 = rotation.m12 * scale
    self.m13 = rotation.m13 * scale
    self.m21 = rotation.m21 * scale
    self.m22 = rotation.m22 * scale
    self.m23 = rotation.m23 * scale
    self.m31 = rotation.m31 * scale
    self.m32 = rotation.m32 * scale
    self.m33 = rotation.m33 * scale

def getInverse(self):
    """Get inverse (assuming isScaleRotation is true!)."""
    # transpose inverts rotation but keeps the scale
    # dividing by scale^2 inverts the scale as well
    return self.getTranspose() / (self.m11*self.m11 + self.m12*self.m12 + self.m13*self.m13)

def __mul__(self, x):
    if isinstance(x, (float, int, long)):
        m = self.cls.Matrix33()
        m.m11 = self.m11 * x
        m.m12 = self.m12 * x
        m.m13 = self.m13 * x
        m.m21 = self.m21 * x
        m.m22 = self.m22 * x
        m.m23 = self.m23 * x
        m.m31 = self.m31 * x
        m.m32 = self.m32 * x
        m.m33 = self.m33 * x
        return m
    elif isinstance(x, self.cls.Vector3):
        raise TypeError("matrix*vector not supported; please use left multiplication (vector*matrix)")
    elif isinstance(x, self.cls.Matrix33):
        m = self.cls.Matrix33()
        m.m11 = self.m11 * x.m11  +  self.m12 * x.m21  +  self.m13 * x.m31 
        m.m12 = self.m11 * x.m12  +  self.m12 * x.m22  +  self.m13 * x.m32 
        m.m13 = self.m11 * x.m13  +  self.m12 * x.m23  +  self.m13 * x.m33 
        m.m21 = self.m21 * x.m11  +  self.m22 * x.m21  +  self.m23 * x.m31 
        m.m22 = self.m21 * x.m12  +  self.m22 * x.m22  +  self.m23 * x.m32 
        m.m23 = self.m21 * x.m13  +  self.m22 * x.m23  +  self.m23 * x.m33 
        m.m31 = self.m31 * x.m11  +  self.m32 * x.m21  +  self.m33 * x.m31 
        m.m32 = self.m31 * x.m12  +  self.m32 * x.m22  +  self.m33 * x.m32 
        m.m33 = self.m31 * x.m13  +  self.m32 * x.m23  +  self.m33 * x.m33
        return m
    else:
        raise TypeError("do not know how to multiply Matrix33 with %s"%x.__class__)

def __div__(self, x):
    if isinstance(x, (float, int, long)):
        m = self.cls.Matrix33()
        m.m11 = self.m11 / x
        m.m12 = self.m12 / x
        m.m13 = self.m13 / x
        m.m21 = self.m21 / x
        m.m22 = self.m22 / x
        m.m23 = self.m23 / x
        m.m31 = self.m31 / x
        m.m32 = self.m32 / x
        m.m33 = self.m33 / x
        return m
    else:
        raise TypeError("do not know how to divide Matrix33 by %s"%x.__class__)

def __rmul__(self, x):
    if isinstance(x, (float, int, long)):
        return self * x
    else:
        raise TypeError("do not know how to multiply %s with Matrix33"%x.__class__)

def __eq__(self, m):
    if abs(self.m11 - m.m11) > self.cls._EPSILON: return False
    if abs(self.m12 - m.m12) > self.cls._EPSILON: return False
    if abs(self.m13 - m.m13) > self.cls._EPSILON: return False
    if abs(self.m21 - m.m21) > self.cls._EPSILON: return False
    if abs(self.m22 - m.m22) > self.cls._EPSILON: return False
    if abs(self.m23 - m.m23) > self.cls._EPSILON: return False
    if abs(self.m31 - m.m31) > self.cls._EPSILON: return False
    if abs(self.m32 - m.m32) > self.cls._EPSILON: return False
    if abs(self.m33 - m.m33) > self.cls._EPSILON: return False
    return True

def __ne__(self, m):
    return not self.__eq__(m)
