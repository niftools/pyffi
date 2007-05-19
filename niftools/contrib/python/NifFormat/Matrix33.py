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
    if abs(m.m12) + abs(m.m13) + abs(m.m21) + abs(m.m23) + abs(m.m31) + abs(m.m32) > 0.0001:
        return False

    # diagonal elements should be equal (to scale^2)
    if abs(m.m11 - m.m22) + abs(m.m22 - m.m33) > 0.0001:
        return False

def isRotation(self):
    """Returns true if the matrix is a rotation matrix."""
    if not self.isScaleRotation(): return False
    if abs(self.scale - 1.0) > 0.0001: return False
    return True

def _get_scale(self):
    return (m.m11*m.m11 + m.m12*m.m12 + m.m13*m.m13) ** 0.5

def _set_scale(self, scale):
    if not isinstance(scale, float):
        raise TypeError('scale must be of type float')
    self *= scale / self.scale

def _get_rotation(self):
    m = self.getCopy()
    s = self.scale
    m.m11 /= s
    m.m12 /= s
    m.m13 /= s
    m.m21 /= s
    m.m22 /= s
    m.m23 /= s
    m.m31 /= s
    m.m32 /= s
    m.m33 /= s
    return m

def _set_rotation(self, m):
    if not isinstance(m, self.cls.Matrix33):
        raise TypeError('argument must be of type Matrix33')
    if not m.isRotation():
        raise ValueError('argument must be a rotation matrix')
    s = self.scale
    self.m11 = m.m11 * s
    self.m12 = m.m12 * s
    self.m13 = m.m13 * s
    self.m21 = m.m21 * s
    self.m22 = m.m22 * s
    self.m23 = m.m23 * s
    self.m31 = m.m31 * s
    self.m32 = m.m32 * s
    self.m33 = m.m33 * s

def __mul__(self, x):
    if isinstance(x, (float, int, long)):
        m = self.cls.Matrix33()
        m.m11 = self.m11 * x
        m.m12 = self.m11 * x
        m.m13 = self.m11 * x
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
    else:
        raise TypeError("do not know how to multiply Matrix33 with %s"%x.__class__)

def __rmul__(self, x):
    if isinstance(x, (float, int, long)):
        return self * x
    elif isinstance(x, self.cls.Vector3):
        v = self.cls.Vector3()
        v.x = x.x * self.m11 + x.y * self.m21 + x.z * self.m31
        v.y = x.x * self.m12 + x.y * self.m22 + x.z * self.m32
        v.z = x.x * self.m13 + x.y * self.m23 + x.z * self.m33
        return v
    else:
        raise TypeError("do not know how to multiply %s with Matrix33"%x.__class__)
