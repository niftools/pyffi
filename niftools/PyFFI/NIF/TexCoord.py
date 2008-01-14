# --------------------------------------------------------------------------
# NifFormat.TexCoord
# Custom functions for TexCoord.
# --------------------------------------------------------------------------
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
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

def asList(self):
    return [self.u, self.v]

def normalize(self):
    r = (self.u*self.u + self.v*self.v) ** 0.5
    if r < self.cls._EPSILON:
        raise ZeroDivisionError('cannot normalize vector %s'%self)
    self.u /= r
    self.v /= r

def __str__(self):
    return "[ %6.3f %6.3f ]"%(self.u, self.v)

def __mul__(self, x):
    if isinstance(x, (float, int, long)):
        v = self.cls.TexCoord()
        v.u = self.u * x
        v.v = self.v * x
        return v
    elif isinstance(x, self.cls.TexCoord):
        return self.u * x.u + self.v * x.v
    else:
        raise TypeError("do not know how to multiply TexCoord with %s"%x.__class__)

def __rmul__(self, x):
    if isinstance(x, (float, int, long)):
        v = self.cls.TexCoord()
        v.u = x * self.u
        v.v = x * self.v
        return v
    else:
        raise TypeError("do not know how to multiply %s and TexCoord"%x.__class__)

def __add__(self, x):
    if isinstance(x, (float, int, long)):
        v = self.cls.TexCoord()
        v.u = self.u + x
        v.v = self.v + x
        return v
    elif isinstance(x, self.cls.TexCoord):
        v = self.cls.TexCoord()
        v.u = self.u + x.u
        v.v = self.v + x.v
        return v
    else:
        raise TypeError("do not know how to add TexCoord and %s"%x.__class__)

def __radd__(self, x):
    if isinstance(x, (float, int, long)):
        v = self.cls.TexCoord()
        v.u = x + self.u
        v.v = x + self.v
        return v
    else:
        raise TypeError("do not know how to add %s and TexCoord"%x.__class__)

def __sub__(self, x):
    if isinstance(x, (float, int, long)):
        v = self.cls.TexCoord()
        v.u = self.u - x
        v.v = self.v - x
        return v
    elif isinstance(x, self.cls.TexCoord):
        v = self.cls.TexCoord()
        v.u = self.u - x.u
        v.v = self.v - x.v
        return v
    else:
        raise TypeError("do not know how to substract TexCoord and %s"%x.__class__)

def __rsub__(self, x):
    if isinstance(x, (float, int, long)):
        v = self.cls.TexCoord()
        v.u = x - self.u
        v.v = x - self.v
        return v
    else:
        raise TypeError("do not know how to substract %s and TexCoord"%x.__class__)

def __neg__(self):
    v = self.cls.TexCoord()
    v.u = -self.u
    v.v = -self.v
    return v
