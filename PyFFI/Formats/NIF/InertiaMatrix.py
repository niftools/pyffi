"""Custom functions for InertiaMatrix."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, NIF File Format Library and Tools.
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
    self.m14 = 0.0
    self.m21 = 0.0
    self.m22 = 1.0
    self.m23 = 0.0
    self.m24 = 0.0
    self.m31 = 0.0
    self.m32 = 0.0
    self.m33 = 1.0
    self.m34 = 0.0

def isIdentity(self):
    """Return C{True} if the matrix is close to identity."""
    if  (abs(self.m11 - 1.0) > self.cls._EPSILON
         or abs(self.m12) > self.cls._EPSILON
         or abs(self.m13) > self.cls._EPSILON
         or abs(self.m21) > self.cls._EPSILON
         or abs(self.m22 - 1.0) > self.cls._EPSILON
         or abs(self.m23) > self.cls._EPSILON
         or abs(self.m31) > self.cls._EPSILON
         or abs(self.m32) > self.cls._EPSILON
         or abs(self.m33 - 1.0) > self.cls._EPSILON):
        return False
    else:
        return True

def getCopy(self):
    """Return a copy of the matrix."""
    mat = self.cls.InertiaMatrix()
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
    return mat

def __eq__(self, mat):
    if not isinstance(mat, self.cls.InertiaMatrix):
        raise TypeError(
            "do not know how to compare InertiaMatrix and %s"%mat.__class__)
    if (abs(self.m11 - mat.m11) > self.cls._EPSILON
        or abs(self.m12 - mat.m12) > self.cls._EPSILON
        or abs(self.m13 - mat.m13) > self.cls._EPSILON
        or abs(self.m21 - mat.m21) > self.cls._EPSILON
        or abs(self.m22 - mat.m22) > self.cls._EPSILON
        or abs(self.m23 - mat.m23) > self.cls._EPSILON
        or abs(self.m31 - mat.m31) > self.cls._EPSILON
        or abs(self.m32 - mat.m32) > self.cls._EPSILON
        or abs(self.m33 - mat.m33) > self.cls._EPSILON):
        return False
    return True

def __ne__(self, mat):
    return not self.__eq__(mat)
