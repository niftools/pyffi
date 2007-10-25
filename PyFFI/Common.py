"""
Implements common basic types in XML file format descriptions.
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, Python File Format Interface.
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
#    * Neither the name of the Python File Format Interface
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

import struct
from Bases.Basic import BasicBase

class Int(BasicBase):
    """Basic implementation of a 32-bit signed integer type. Also serves as a
    base class for all other integer types.

    >>> from tempfile import TemporaryFile
    >>> tmp = TemporaryFile()
    >>> i = Int()
    >>> i.setValue(-1)
    >>> i.getValue()
    -1
    >>> i.setValue(0x11223344)
    >>> i.write(f = tmp)
    >>> j = Int()
    >>> tmp.seek(0)
    >>> j.read(f = tmp)
    >>> hex(j.getValue())
    '0x11223344'
    >>> i.setValue(0x10000000000L) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...
    >>> i.setValue('hello world')
    Traceback (most recent call last):
        ...
    ValueError: cannot convert value 'hello world' to integer
    >>> tmp.seek(0)
    >>> tmp.write('\x11\x22\x33\x44')
    >>> tmp.seek(0)
    >>> i.read(f = tmp)
    >>> hex(i.getValue())
    '0x44332211'
    """
    
    _min = -0x80000000 #: Minimum value.
    _max = 0x7fffffff  #: Maximum value.
    _struct = 'i'      #: Character used to represent type in struct.
    _size = 4          #: Number of bytes.

    def __init__(self, **kwargs):
        self._x = ''.join(['\x00' for i in xrange(self._size)])
        #self.setValue(0L)

    def getValue(self):
        return struct.unpack('<' + self._struct, self._x)[0]

    def setValue(self, value):
        try:
            x = int(value)
        except ValueError:
            try:
                x = int(value, 16) # for '0x...' strings
            except:
                try:
                    x = getattr(self, value) # for enums
                except:
                    raise ValueError("cannot convert value '%s' to integer"%str(value))
        if x < self._min or x > self._max:
            raise ValueError('value out of range (%i)'%self.getValue())
        self._x = struct.pack('<' + self._struct, x)

    def read(self, f = None, **kwargs):
        # file must be an instance of the type
        self._x = f.read(self._size)

    def write(self, f = None, **kwargs):
        f.write(self._x)

    def __str__(self):
        return str(self.getValue())

    def getSize(self, **kwargs):
        return self._size

    def getHash(self, **kwargs):
        return self.getValue()

class UInt(Int):
    _min = 0
    _max = 0xffffffff
    _struct = 'I'
    _size = 4

class Byte(Int):
    _min = -0x80
    _max = 0x7f
    _struct = 'b'
    _size = 1

class UByte(Int):
    _min = 0
    _max = 0xff
    _struct = 'B'
    _size = 1

class Short(Int):
    _min = -0x8000
    _max = 0x7fff
    _struct = 'h'
    _size = 2

class UShort(UInt):
    _min = 0
    _max = 0xffff
    _struct = 'H'
    _size = 2

class Char(BasicBase):
    def __init__(self, **kwargs):
        self.setValue('\x00')

    def getValue(self):
        return self._x

    def setValue(self, value):
        assert(isinstance(value, str))
        assert(len(value) == 1)
        self._x = value

    def read(self, f = None, **kwargs):
        self._x = f.read(1)

    def write(self, f = None, **kwargs):
        f.write(self._x)

    def __str__(self):
        return self._x

    def getSize(self, **kwargs):
        return 1

    def getHash(self, **kwargs):
        self.getValue()

class Float(BasicBase):
    def __init__(self, **kwargs):
        self._x = '\x00\x00\x00\x00'

    def getValue(self):
        return struct.unpack('<f', self._x)[0]

    def setValue(self, value):
        self._x = struct.pack('<f', float(value))

    def read(self, f = None, **kwargs):
        self._x = f.read(4)

    def write(self, f = None, **kwargs):
        f.write(self._x)

    def getSize(self, **kwargs):
        return 4

    def getHash(self, **kwargs):
        return int(self.getValue()*200)

### faster calculation, slower read/write:
##class Float(BasicBase):
##    def __init__(self, **kwargs):
##        self._x = 0.0
##
##    def getValue(self):
##        return self._x
##
##    def setValue(self, value):
##        self._x = float(value)
##
##    def read(self, f = None, **kwargs):
##        self._x = struct.unpack('<f', f.read(4))[0]
##
##    def write(self, f = None, **kwargs):
##        f.write(struct.pack('<f', self._x))
