# --------------------------------------------------------------------------
# NifFormat.BasicTypes
# Implementation of all basic types in the xml NIF file format description.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2005, NIF File Format Library and Tools.
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

from FileFormat.Bases.Basic import BasicBase

class Int(BasicBase):
    _isTemplate = False

    def __init__(self):
        self.setValue(0L)

    def getValue(self):
        return self._x

    def setValue(self, value):
        try:
            self._x = long(value)
        except ValueError:
            try:
                self._x = long(value, 16) # for '0x...' strings
            except:
                raise ValueError("cannot convert value '%s' to integer"%str(value))

class UInt(Int):
    _isTemplate = False

    def setValue(self, value):
        Int.setValue(self, value)
        if self._x < 0:
            raise ValueError("negative UInt (%i)"%self._x)

class Bool(Int):
    _isTemplate = False

    def __init__(self):
        self.setValue(False)

    def setValue(self, value):
        if value:
            self._x = True
        else:
            self._x = False

class Byte(Int):
    _isTemplate = False
    
    def setValue(self, value):
        Int.setValue(self, value)
        if self._x < 0 or self._x > 255:
            raise ValueError('Byte out of range (%i)'%self.getValue())

# TODO
class Char(Int):
    _isTemplate = False
    def __init__(self):
        self.setValue('\x00')

    def setValue(self, value):
        assert(isinstance(value, str))
        assert(len(value) == 1)
        self._x = value

class Short(Int):
    _isTemplate = False

    def setValue(self, value):
        Int.setValue(self, value)
        if self._x < -32768 or self._x > 32767:
            raise ValueError('Byte out of range (%i)'%self.getValue())

class UShort(UInt):
    _isTemplate = False

    def setValue(self, value):
        Int.setValue(self, value)
        if self._x < 0 or self._x > 65535:
            raise ValueError('UShort out of range (%i)'%self.getValue())

# TODO
class Flags(UShort):
    _isTemplate = False

    def __str__(self):
        return hex(self.getValue())

class Float(Int):
    _isTemplate = False
    def __init__(self):
        self.setValue(0.0)

    def setValue(self, value):
        self._x = float(value)

class Ref(BasicBase):
    _isTemplate = True
    def __init__(self, tmpl):
        self._template = tmpl
        self.setValue(None)

    def getValue(self):
        return self._x

    def setValue(self, value):
        if value == None:
            self._x = None
        else:
            #assert(isinstance(value, self._template)) # uncomment when forwards are resolved
            self._x = value

class Ptr(Ref):
    _isTemplate = True

    def __str__(self):
        # avoid infinite recursion
        return '%s instance at 0x%08X'%(self._x.__class__, id(self._x))

class LineString(BasicBase):
    _isTemplate = False
    def __init__(self):
        self.setValue('')

    def getValue(self):
        return self._x

    def setValue(self, value):
        self._x = str(value)

    def __str__(self):
        s = BasicBase.__str__(self)
        if not s: return '<EMPTY STRING>'
        return "'" + s + "'"
