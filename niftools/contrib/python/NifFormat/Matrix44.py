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

def getTranslation(self):
    """Returns lower left 1x3 part."""
    t = self.cls.Vector3()
    t.x = self.m41
    t.y = self.m42
    t.z = self.m43
    return t

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

    self.m11 = rotation.m11 * scale
    self.m12 = rotation.m12 * scale
    self.m13 = rotation.m13 * scale
    self.m21 = rotation.m21 * scale
    self.m22 = rotation.m22 * scale
    self.m23 = rotation.m23 * scale
    self.m31 = rotation.m31 * scale
    self.m32 = rotation.m32 * scale
    self.m33 = rotation.m33 * scale

    self.m41 = translation.x
    self.m42 = translation.y
    self.m43 = translation.z

    self.m14 = 0.0
    self.m24 = 0.0
    self.m34 = 0.0
    self.m44 = 1.0
