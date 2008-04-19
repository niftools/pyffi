"""Implements common basic types in XML file format descriptions."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface.
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
# ***** END LICENSE BLOCK *****

import struct
from itertools import izip
from PyFFI.Bases.Basic import BasicBase, FloatBase
from PyFFI.Bases.Delegate import DelegateSpinBox
from PyFFI.Bases.Delegate import DelegateFloatSpinBox
from PyFFI.Bases.Delegate import DelegateLineEdit
from PyFFI.Bases.Delegate import DelegateBoolComboBox

class Int(BasicBase, DelegateSpinBox):
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
    _default = ''.join('\x00' for i in xrange(_size)) #: Default value (in internal storage format).

    def __init__(self, **kwargs):
        super(Int, self).__init__(**kwargs)
        self._value = ''.join('\x00' for i in xrange(self._size)) #self._default

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
            raise ValueError('value out of range (%i)' % val)
        self._value = struct.pack('<' + self._struct, val)

    def read(self, stream, **kwargs):
        """Read value from stream."""
        self._value = stream.read(self._size)

    def write(self, stream, **kwargs):
        """Write value to stream."""
        stream.write(self._value)

    def __str__(self):
        return str(self.getValue())

    @classmethod
    def getSize(cls, **kwargs):
        """Return size of this type."""
        return cls._size

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self.getValue()

    def qDelegateMinimum(self):
        return self._min

    def qDelegateMaximum(self):
        return self._max

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

class Bool(UByte, DelegateBoolComboBox):
    """Simple bool implementation."""
    def getValue(self):
        return False if self._value == '\x00' else True

    def setValue(self, value):
        self._value = '\x01' if value else '\x00'

class Char(BasicBase, DelegateLineEdit):
    """Implementation of an 8-bit ASCII character."""
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

class Float(FloatBase, DelegateFloatSpinBox):
    """Implementation of a 32-bit float."""
    pass

class ZString(BasicBase, DelegateLineEdit):
    """String of variable length (null terminated).

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> s = ZString()
    >>> f.write('abcdefghijklmnopqrst\\x00')
    >>> f.seek(0)
    >>> s.read(f)
    >>> str(s)
    'abcdefghijklmnopqrst'
    >>> f.seek(0)
    >>> s.setValue('Hi There!')
    >>> s.write(f)
    >>> f.seek(0)
    >>> m = ZString()
    >>> m.read(f)
    >>> str(m)
    'Hi There!'
    """
    _maxlen = 1000 #: The maximum length.
    
    def __init__(self, **kwargs):
        super(ZString, self).__init__(**kwargs)
        self._value = ""

    def __str__(self):
        if not self._value:
            return '<EMPTY STRING>'
        return self._value

    def getValue(self):
        """Return the string."""
        return self._value

    def setValue(self, value):
        """Set the string."""
        val = str(value)
        i = val.find('\x00')
        if i != -1:
            val = val[:i]
        if len(val) > self._maxlen:
            raise ValueError('string too long')
        self._value = val

    def read(self, stream, **kwargs):
        """Read string from stream."""
        i = 0
        self._value = ''
        char = ''
        while char != '\x00':
            i += 1
            if i > self._maxlen:
                raise ValueError('string too long')
            self._value += char
            char = stream.read(1)

    def write(self, stream, **kwargs):
        """Write string to stream."""
        stream.write(self._value)
        stream.write('\x00')

    def getSize(self, **kwargs):
        """Return string size in bytes."""
        return len(self._value) + 1

    def getHash(self, **kwargs):
        """Return hash value for the string."""
        return self._value

class FixedString(BasicBase, DelegateLineEdit):
    """String of fixed length. Default length is 0, so you must override
    this class and set the _len class variable.

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> class String8(FixedString):
    ...     _len = 8
    >>> s = String8()
    >>> f.write('abcdefghij')
    >>> f.seek(0)
    >>> s.read(f)
    >>> str(s)
    'abcdefgh'
    >>> f.seek(0)
    >>> s.setValue('Hi There')
    >>> s.write(f)
    >>> f.seek(0)
    >>> m = String8()
    >>> m.read(f)
    >>> str(m)
    'Hi There'
    """
    _len = 0
    
    def __init__(self, **kwargs):
        super(FixedString, self).__init__(**kwargs)
        self._value = ""

    def __str__(self):
        if not self._value:
            return '<EMPTY STRING>'
        return self._value

    def getValue(self):
        """Return the string."""
        return self._value

    def setValue(self, value):
        """Set the string."""
        val = str(value)
        if len(val) > self._len:
            raise ValueError("string '%s' too long" % val)
        self._value = val

    def read(self, stream, **kwargs):
        """Read string from stream."""
        self._value = stream.read(self._len)
        i = self._value.find('\x00')
        if i != -1:
            self._value = self._value[:i]

    def write(self, stream, **kwargs):
        """Write string to stream."""
        stream.write(self._value.ljust(self._len, "\x00"))

    def getSize(self, **kwargs):
        """Return string size in bytes."""
        return self._len

    def getHash(self, **kwargs):
        """Return hash value for the string."""
        return self._value

class SizedString(BasicBase, DelegateLineEdit):
    """Basic type for strings. The type starts with an unsigned int which
    describes the length of the string.

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> s = SizedString()
    >>> f.write('\\x07\\x00\\x00\\x00abcdefg')
    >>> f.seek(0)
    >>> s.read(f)
    >>> str(s)
    'abcdefg'
    >>> f.seek(0)
    >>> s.setValue('Hi There')
    >>> s.write(f)
    >>> f.seek(0)
    >>> m = SizedString()
    >>> m.read(f)
    >>> str(m)
    'Hi There'
    """
    def __init__(self, **kwargs):
        BasicBase.__init__(self, **kwargs)            
        self._value = ""

    def getValue(self):
        return self._value

    def setValue(self, value):
        if len(value) > 10000:
            raise ValueError('string too long')
        self._value = str(value)

    def __str__(self):
        s = self._value
        if not s:
            return '<EMPTY STRING>'
        return s

    def getSize(self, **kwargs):
        return 4 + len(self._value)

    def getHash(self, **kwargs):
        return self.getValue()

    def read(self, stream, **kwargs):
        n, = struct.unpack('<I', stream.read(4))
        if n > 10000:
            raise ValueError('string too long (0x%08X at 0x%08X)'
                             % (n, stream.tell()))
        self._value = stream.read(n)

    def write(self, stream, **kwargs):
        stream.write(struct.pack('<I', len(self._value)))
        stream.write(self._value)


