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

def _get_matrix33(self):
    """Returns upper left 3x3 part. If you change attributes of this element,
    then you also change the original 4x4 matrix."""
    m = self.cls.Matrix33()
    # copy the actual instances rather than the wrapped values
    m._m11_value_ = self._m11_value_
    m._m12_value_ = self._m12_value_
    m._m13_value_ = self._m13_value_
    m._m21_value_ = self._m21_value_
    m._m22_value_ = self._m22_value_
    m._m23_value_ = self._m23_value_
    m._m31_value_ = self._m31_value_
    m._m32_value_ = self._m32_value_
    m._m33_value_ = self._m33_value_
    return m

def _set_matrix33(self, m):
    if not isinstance(m, cls.Matrix33):
        raise TypeError("argument must be of the Matrix33 type")
    self.m11 = m.m11
    self.m12 = m.m12
    self.m13 = m.m13
    self.m21 = m.m21
    self.m22 = m.m22
    self.m23 = m.m23
    self.m31 = m.m31
    self.m32 = m.m32
    self.m33 = m.m33

def _get_scale(self):
    return self.matrix33.scale

def _set_scale(self, scale):
    self.matrix33.scale = scale

def _get_rotation(self):
    return self.matrix33.rotation

def _set_rotation(self, m):
    self.matrix33.rotation = m

def _get_translation(self):
    """Returns lower left 1x3 part. If you change attributes of this element,
    then you also change the original 4x4 matrix."""
    t = self.cls.Vector3()
    t._x_value_ = self._m41_value_
    t._y_value_ = self._m42_value_
    t._z_value_ = self._m43_value_
    return t

def _set_translation(self, t):
    if not isinstance(t, self.cls.Vector3):
        raise TypeError("argument must be of the Vector3 type")

