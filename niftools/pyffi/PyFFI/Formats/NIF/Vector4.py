"""Custom functions for Vector4."""

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

def asList(self):
    return [self.x, self.y, self.z, self.w]

def asTuple(self):
    return (self.x, self.y, self.z, self.w)

def getCopy(self):
    v = self.cls.Vector4()
    v.x = self.x
    v.y = self.y
    v.z = self.z
    v.w = self.w
    return v

def getVector3(self):
    v = self.cls.Vector3()
    v.x = self.x
    v.y = self.y
    v.z = self.z
    return v

def __str__(self):
    return "[ %6.3f %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z, self.w)

def __eq__(self, rhs):
    if isinstance(rhs, NoneType):
        return False
    if not isinstance(rhs, self.cls.Vector4):
        raise TypeError(
            "do not know how to compare Vector4 and %s" % rhs.__class__)
    if abs(self.x - rhs.x) > self.cls._EPSILON: return False
    if abs(self.y - rhs.y) > self.cls._EPSILON: return False
    if abs(self.z - rhs.z) > self.cls._EPSILON: return False
    if abs(self.w - rhs.w) > self.cls._EPSILON: return False
    return True

def __ne__(self, rhs):
    return not self.__eq__(rhs)
