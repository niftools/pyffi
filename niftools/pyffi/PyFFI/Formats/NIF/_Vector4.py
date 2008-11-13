"""Custom functions for Vector4.

Doctests
========

>>> from PyFFI.Formats.NIF import NifFormat
>>> vec = NifFormat.Vector4()
>>> vec.x = 1.0
>>> vec.y = 2.0
>>> vec.z = 3.0
>>> vec.w = 4.0
>>> print(vec)
[  1.000  2.000  3.000  4.000 ]
>>> vec.asList()
[1.0, 2.0, 3.0, 4.0]
>>> vec.asTuple()
(1.0, 2.0, 3.0, 4.0)
>>> print(vec.getVector3())
[  1.000  2.000  3.000 ]
>>> vec2 = NifFormat.Vector4()
>>> vec == vec2
False
>>> vec2.x = 1.0
>>> vec2.y = 2.0
>>> vec2.z = 3.0
>>> vec2.w = 4.0
>>> vec == vec2
True
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, NIF File Format Library and Tools.
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

from types import NoneType

from PyFFI.Formats.NIF._NifFormat import NifFormat
from PyFFI.Utils.Partial import MetaPartial


class _Vector4(NifFormat.Vector4):
    __metaclass__ = MetaPartial

    def asList(self):
        return [self.x, self.y, self.z, self.w]

    def asTuple(self):
        return (self.x, self.y, self.z, self.w)

    def getCopy(self):
        v = NifFormat.Vector4()
        v.x = self.x
        v.y = self.y
        v.z = self.z
        v.w = self.w
        return v

    def getVector3(self):
        v = NifFormat.Vector3()
        v.x = self.x
        v.y = self.y
        v.z = self.z
        return v

    def __str__(self):
        return "[ %6.3f %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z, self.w)

    def __eq__(self, rhs):
        if isinstance(rhs, NoneType):
            return False
        if not isinstance(rhs, NifFormat.Vector4):
            raise TypeError(
                "do not know how to compare Vector4 and %s" % rhs.__class__)
        if abs(self.x - rhs.x) > NifFormat._EPSILON: return False
        if abs(self.y - rhs.y) > NifFormat._EPSILON: return False
        if abs(self.z - rhs.z) > NifFormat._EPSILON: return False
        if abs(self.w - rhs.w) > NifFormat._EPSILON: return False
        return True

    def __ne__(self, rhs):
        return not self.__eq__(rhs)
