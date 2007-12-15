"""Implements common basic types in XML file format descriptions."""

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
from itertools import izip
from PyFFI.Bases.Basic import BasicBase

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
    >>> i.write(tmp)
    >>> j = Int()
    >>> tmp.seek(0)
    >>> j.read(tmp)
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
    >>> i.read(tmp)
    >>> hex(i.getValue())
    '0x44332211'
    """
    
    _min = -0x80000000 #: Minimum value.
    _max = 0x7fffffff  #: Maximum value.
    _struct = 'i'      #: Character used to represent type in struct.
    _size = 4          #: Number of bytes.

    def __init__(self, **kwargs):
        super(Int, self).__init__(**kwargs)
        self._value = ''.join('\x00' for i in xrange(self._size))

    def getValue(self):
        """Return stored value."""
        return struct.unpack('<' + self._struct, self._value)[0]

    def setValue(self, value):
        """Set value to C{value}."""
        try:
            val = int(value)
        except ValueError:
            try:
                val = int(value, 16) # for '0x...' strings
            except ValueError:
                try:
                    val = getattr(self, value) # for enums
                except AttributeError:
                    raise ValueError(
                        "cannot convert value '%s' to integer"%value)
        if val < self._min or val > self._max:
            raise ValueError('value out of range (%i)'%self.getValue())
        self._value = struct.pack('<' + self._struct, val)

    def read(self, stream, **kwargs):
        """Read value from stream."""
        self._value = stream.read(self._size)

    def write(self, stream, **kwargs):
        """Write value to stream."""
        stream.write(self._value)

    def __str__(self):
        return str(self.getValue())

    def getSize(self, **kwargs):
        """Return size of this type."""
        return self._size

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self.getValue()

class UInt(Int):
    """Implementation of a 32-bit unsigned integer type."""
    _min = 0
    _max = 0xffffffff
    _struct = 'I'
    _size = 4

class Byte(Int):
    """Implementation of a 8-bit signed integer type."""
    _min = -0x80
    _max = 0x7f
    _struct = 'b'
    _size = 1

class UByte(Int):
    """Implementation of a 8-bit unsigned integer type."""
    _min = 0
    _max = 0xff
    _struct = 'B'
    _size = 1

class Short(Int):
    """Implementation of a 16-bit signed integer type."""
    _min = -0x8000
    _max = 0x7fff
    _struct = 'h'
    _size = 2

class UShort(UInt):
    """Implementation of a 16-bit unsigned integer type."""
    _min = 0
    _max = 0xffff
    _struct = 'H'
    _size = 2

class Char(BasicBase):
    """Implementation of an 8-bit ACII character."""
    def __init__(self, **kwargs):
        super(Char, self).__init__(**kwargs)
        self._value = '\x00'

    def getValue(self):
        """Return stored value."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        assert(isinstance(value, basestring))
        assert(len(value) == 1)
        self._value = str(value)

    def read(self, stream, **kwargs):
        """Read value from stream."""
        self._value = stream.read(1)

    def write(self, stream, **kwargs):
        """Write value to stream."""
        stream.write(self._value)

    def __str__(self):
        return self._value

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 1

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        self.getValue()

class Float(BasicBase):
    """Implementation of a 32-bit float."""
    def __init__(self, **kwargs):
        super(Float, self).__init__(**kwargs)
        self._value = '\x00\x00\x00\x00'

    def getValue(self):
        """Return stored value."""
        return struct.unpack('<f', self._value)[0]

    def setValue(self, value):
        """Set value to C{value}."""
        self._value = struct.pack('<f', float(value))

    def read(self, stream, **kwargs):
        """Read value from stream."""
        self._value = stream.read(4)

    def write(self, stream, **kwargs):
        """Write value to stream."""
        stream.write(self._value)

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 4

    def getHash(self, **kwargs):
        """Return a hash value for this value. Currently implemented
        with precision 1/200."""
        return int(self.getValue()*200)

class VectorBase(BasicBase):
    """Implementation of a N-dimensional vector.

    Use as base class for vectors and set the C{_dim} class variable to the
    dimension and the C{_type} class variable to the actual vector type that
    should do the math. The constructor of C{_type} must take C{_dim} float
    arguments, and C{_type} must be iterable. For example, the
    Blender.Mathutils.Vector class satisfies these requirements."""
    _dim  = 3
    _type = tuple

    def __init__(self, **kwargs):
        super(VectorBase, self).__init__(**kwargs)
        self._value = self._type(*tuple(0.0 for i in xrange(self._dim)))

    def getValue(self):
        """Return stored value as a C{self._type} type."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        if not isinstance(value, self._type):
            raise TypeError("Argument must be of type %s."
                            % self._type.__class__)
        if not len(value) != self._dim:
            raise TypeError("Argument must have length %i." % self._dim)
        self._value = value

    def __str__(self):
        return ("[ " + "%6.3f " * self._dim + "]") % tuple(self._value)

    def read(self, stream, **kwargs):
        """Read value from stream."""
        self._value = self._type(*tuple(struct.unpack("<f", stream.read(4))
                                        for i in xrange(self._dim)))

    def write(self, stream, **kwargs):
        """Write value to stream."""
        for elem in self._value:
            stream.write(struct.pack("<f", elem))

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 4 * self._dim

    def getHash(self, **kwargs):
        """Return a hash value for this vector. Currently implemented
        with precision 1/200."""
        return tuple(int(x * 200) for x in self._value)

class MatrixBase(BasicBase):
    """Implementation of a nxm matrix.

    Use as base class for matrices and set the C{_dim_n} and C{_dim_m} class
    variables to the dimensions and the C{_type} class variable to the actual
    matrix type that should do the math. The constructor of C{_type} must take
    {_dim_n} arguments, each of which is a tuple of C{_dim_m} floats. If the
    matrix is stored transposed, then set C{_transposed} to C{True}."""
    _dim_n = 3
    _dim_m = 3
    _type = tuple
    _transposed = False

    def __init__(self, **kwargs):
        super(MatrixBase, self).__init__(**kwargs)
        self._value = self._type(*( tuple( 0.0
                                           for j in xrange(self._dim_m) )
                                    for i in xrange(self._dim_n) ) )

    def getValue(self):
        """Return stored matrix."""
        return self._value

    def setValue(self, value):
        """Set matrix to C{value}."""
        # check type
        if not isinstance(value, self._type):
            raise TypeError("Argument must be of type %s."
                            % self._type.__class__)
        # set the value
        self._value = value

    def __str__(self):
        result = ""
        for row in self._value:
            result += ("[ " + "%6.3f " * len(row) + "]\n") % row
        return result

    def read(self, stream, **kwargs):
        """Read matrix from stream."""
        if not self._transposed:
            mat = ( struct(unpack("<" + "f" * self._dim_m,
                                  stream.read(4 * self._dim_m)))
                    for i in xrange(self._dim_n) )
            self._value = self._type(*mat)
        else:
            mat = ( struct(unpack("<" + "f" * self._dim_n,
                                  stream.read(4 * self._dim_n)))
                    for i in xrange(self._dim_m) )
            # izip(*mat) is an iterator which transposes the matrix
            self._value = self._type(*izip(*mat))

    def write(self, stream, **kwargs):
        """Write matrix to stream."""
        if not self._transposed:
            for row in mat:
                stream.write(struct.pack("<" + "f" * len(row), *row))
        else:
            for row in izip(*mat):
                stream.write(struct.pack("<" + "f" * len(row), *row))

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 4 * self._dim_n * self._dim_m

    def getHash(self, **kwargs):
        """Return a hash value for this matrix. Currently implemented
        with precision 1/200."""
        return tuple( tuple( int(elem * 200) for elem in row )
                      for row in self._value )
