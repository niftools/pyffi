"""Custom functions for Vector3."""

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

from types import *

from PyFFI.Formats.NIF._NifFormat import NifFormat
from PyFFI.Utils.Partial import MetaPartial

class _Vector3(NifFormat.Vector3):
    __metaclass__ = MetaPartial

    def asList(self):
        return [self.x, self.y, self.z]

    def asTuple(self):
        return (self.x, self.y, self.z)

    def norm(self):
        return (self.x*self.x + self.y*self.y + self.z*self.z) ** 0.5

    def normalize(self):
        norm = self.norm()
        if norm < NifFormat._EPSILON:
            raise ZeroDivisionError('cannot normalize vector %s'%self)
        self.x /= norm
        self.y /= norm
        self.z /= norm

    def getCopy(self):
        v = NifFormat.Vector3()
        v.x = self.x
        v.y = self.y
        v.z = self.z
        return v

    def __str__(self):
        return "[ %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z)

    def __mul__(self, x):
        if isinstance(x, (float, int, long)):
            v = NifFormat.Vector3()
            v.x = self.x * x
            v.y = self.y * x
            v.z = self.z * x
            return v
        elif isinstance(x, NifFormat.Vector3):
            return self.x * x.x + self.y * x.y + self.z * x.z
        elif isinstance(x, NifFormat.Matrix33):
            v = NifFormat.Vector3()
            v.x = self.x * x.m11 + self.y * x.m21 + self.z * x.m31
            v.y = self.x * x.m12 + self.y * x.m22 + self.z * x.m32
            v.z = self.x * x.m13 + self.y * x.m23 + self.z * x.m33
            return v
        elif isinstance(x, NifFormat.Matrix44):
            return self * x.getMatrix33() + x.getTranslation()
        else:
            raise TypeError("do not know how to multiply Vector3 with %s"%x.__class__)

    def __rmul__(self, x):
        if isinstance(x, (float, int, long)):
            v = NifFormat.Vector3()
            v.x = x * self.x
            v.y = x * self.y
            v.z = x * self.z
            return v
        else:
            raise TypeError("do not know how to multiply %s and Vector3"%x.__class__)

    def __div__(self, x):
        if isinstance(x, (float, int, long)):
            v = NifFormat.Vector3()
            v.x = self.x / x
            v.y = self.y / x
            v.z = self.z / x
            return v
        else:
            raise TypeError("do not know how to divide Vector3 and %s"%x.__class__)

    def __add__(self, x):
        if isinstance(x, (float, int, long)):
            v = NifFormat.Vector3()
            v.x = self.x + x
            v.y = self.y + x
            v.z = self.z + x
            return v
        elif isinstance(x, NifFormat.Vector3):
            v = NifFormat.Vector3()
            v.x = self.x + x.x
            v.y = self.y + x.y
            v.z = self.z + x.z
            return v
        else:
            raise TypeError("do not know how to add Vector3 and %s"%x.__class__)

    def __radd__(self, x):
        if isinstance(x, (float, int, long)):
            v = NifFormat.Vector3()
            v.x = x + self.x
            v.y = x + self.y
            v.z = x + self.z
            return v
        else:
            raise TypeError("do not know how to add %s and Vector3"%x.__class__)

    def __sub__(self, x):
        if isinstance(x, (float, int, long)):
            v = NifFormat.Vector3()
            v.x = self.x - x
            v.y = self.y - x
            v.z = self.z - x
            return v
        elif isinstance(x, NifFormat.Vector3):
            v = NifFormat.Vector3()
            v.x = self.x - x.x
            v.y = self.y - x.y
            v.z = self.z - x.z
            return v
        else:
            raise TypeError("do not know how to substract Vector3 and %s"%x.__class__)

    def __rsub__(self, x):
        if isinstance(x, (float, int, long)):
            v = NifFormat.Vector3()
            v.x = x - self.x
            v.y = x - self.y
            v.z = x - self.z
            return v
        else:
            raise TypeError("do not know how to substract %s and Vector3"%x.__class__)

    def __neg__(self):
        v = NifFormat.Vector3()
        v.x = -self.x
        v.y = -self.y
        v.z = -self.z
        return v

    # cross product
    def crossproduct(self, x):
        if isinstance(x, NifFormat.Vector3):
            v = NifFormat.Vector3()
            v.x = self.y*x.z - self.z*x.y
            v.y = self.z*x.x - self.x*x.z
            v.z = self.x*x.y - self.y*x.x
            return v
        else:
            raise TypeError("do not know how to calculate crossproduct of Vector3 and %s"%x.__class__)

    def __eq__(self, x):
        if isinstance(x, NoneType):
            return False
        if not isinstance(x, NifFormat.Vector3):
            raise TypeError("do not know how to compare Vector3 and %s"%x.__class__)
        if abs(self.x - x.x) > NifFormat._EPSILON: return False
        if abs(self.y - x.y) > NifFormat._EPSILON: return False
        if abs(self.z - x.z) > NifFormat._EPSILON: return False
        return True

    def __ne__(self, x):
        return not self.__eq__(x)
