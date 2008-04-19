"""Partial Cython/Pyrex implementation of base classes for basic types.
Use PyFFI.Bases.Basic instead of this module. This module only contains a
partial implementation of the base classes because Cython/Pyrex do not support
class variables and class methods."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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
# --------------------------------------------------------------------------

# C functions we need
cdef extern from "Python.h":
    # low level file access
    ctypedef struct FILE
    FILE* PyFile_AsFile(object)
    int fread(void *ptr, int size, int nitems, FILE *stream)
    int fwrite(void *ptr, int size, int nitems, FILE *stream)
    # convenience conversion functions
    object PyInt_FromLong(int value)

# Cython/Pyrex does not support class variables
# so first we define the classes with class variables
# (these are the "Cxxx" classes)
# then we derive the classes from those, and define
# the class variables in them, in PyFFI.Bases.Basic

cdef class CBasicBase:
    """Base class from which all basic types are derived.
    
    The BasicBase class implements the interface for basic types.
    All basic types are derived from this class.
    They must override read, write, getValue, and setValue.

    >>> import struct
    >>> class UInt(CBasicBase):
    ...     def __init__(self, template = None, argument = 0):
    ...         self.__value = 0
    ...     def read(self, version = None, user_version = None, f = None, link_stack = [], argument = None):
    ...         self.__value, = struct.unpack('<I', f.read(4))
    ...     def write(self, version = None, user_version = None, f = None, block_index_dct = {}, argument = None):
    ...         f.write(struct.pack('<I', self.__value))
    ...     def getValue(self):
    ...         return self.__value
    ...     def setValue(self, value):
    ...         self.__value = int(value)
    >>> x = UInt()
    >>> x.setValue('123')
    >>> x.getValue()
    123
    >>> class Test(CBasicBase): # bad: read, write, getValue, and setValue are not implemented
    ...     pass
    >>> x = Test() # doctest: +ELLIPSIS
    >>> x.setValue('123') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    NotImplementedError
    """

    # class variables not supported by Cython, deferred to BasicBase
    #_isTemplate = False
    #_hasLinks = False
    #_hasRefs = False
    #_hasStrings = False

    cdef object _parent

    def __init__(self, template = None, argument = None, parent = None):
        """Initializes the instance.

        @param template: type used as template
        @param argument: argument used to initialize the instance
            (see the Struct class).
        @param parent: The parent of this instance, that is, the instance this
            instance is an attribute of."""
        self._parent = parent

    # string representation
    def __str__(self):
        """Return string representation."""
        return str(self.getValue())

    def getSize(self, **kwargs):
        """Returns size of the object in bytes."""
        raise NotImplementedError

    def read(self, stream, **kwargs):
        """Read object from file."""
        raise NotImplementedError

    def write(self, stream, **kwargs):
        """Write object to file."""
        raise NotImplementedError

    def fixLinks(self, **kwargs):
        """Fix links. Called when all objects have been read, and converts
        block indices into blocks."""
        pass
    
    def getLinks(self, **kwargs):
        """Return all links referred to in this object."""
        return []
    
    def getStrings(self, **kwargs):
        """Return all strings used by this object."""
        return []
    
    def getRefs(self, **kwargs):
        """Return all references (excluding weak pointers) used by this
        object."""
        return []
    
    def getValue(self):
        """Return object value."""
        raise NotImplementedError

    def setValue(self, value):
        """Set object value."""
        raise NotImplementedError

    def getHash(self, **kwargs):
        """Returns a hash value (an immutable object) that can be used to
        identify the object uniquely."""
        raise NotImplementedError

    #
    # user interface functions come next
    # these functions are named after similar ones in the TreeItem example
    # at http://doc.trolltech.com/4.3/itemviews-simpletreemodel.html
    #

    def qParent(self):
        """Return parent of this structure."""
        return self._parent

    def qChildCount(self):
        """Return number of items in this structure. Always zero for basic
        types."""
        return 0

    def qChild(self, row):
        """Find item at given row. Should never be called."""
        raise NotImplementedError

    def qRow(self, item):
        """Find the row number of the given item. Should never be called."""
        raise NotImplementedError

    def qName(self, item):
        """Find the name of the given item. Should never be called."""
        raise NotImplementedError

    def qDataDisplay(self):
        """Return an object that can be used to display the instance."""
        return self.getValue()

cdef class CFloatBase(CBasicBase):
    """Implementation of a 32-bit float. Note that the float has less
    precision than the Python floats (which are usually 64-bit), so
    for instance assigning 287454020.0 to this type will result in the
    value 287454016.0 due to the 32-bit representation.

    >>> from tempfile import TemporaryFile
    >>> tmp = TemporaryFile()
    >>> i = CFloatBase()
    >>> i.setValue(-1)
    >>> i.getValue()
    -1.0
    >>> i.setValue(3.1415926535)
    >>> i.getValue() # doctest: +ELLIPSIS
    3.141592...
    >>> i.write(tmp)
    >>> j = CFloatBase()
    >>> tmp.seek(0)
    >>> j.read(tmp)
    >>> j.getValue() # doctest: +ELLIPSIS
    3.141592...
    >>> i.setValue('hello world')
    Traceback (most recent call last):
        ...
    TypeError: a float is required
    >>> tmp.seek(0)
    >>> tmp.write('\\x00\\x00\\x80\\x3f')
    >>> tmp.seek(0)
    >>> i.read(tmp)
    >>> i.getValue()
    1.0
    """

    cdef float _value

    def __init__(self, **kwargs):
        self._parent = kwargs.get("parent")
        self._value = 0

    def getValue(self):
        """Return stored value."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        self._value = value

    def read(self, stream, **kwargs):
        """Read value from stream."""
        fread(&self._value, 4, 1, PyFile_AsFile(stream))

    def write(self, stream, **kwargs):
        """Write value to stream."""
        fwrite(&self._value, 4, 1, PyFile_AsFile(stream))

    def __str__(self):
        return str(self._value)

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 4

    def getHash(self, **kwargs):
        """Return a hash value for this value. Currently implemented
        with precision 1/200."""
        return int(self._value * 200)

cdef class CIntBase(CBasicBase):
    """Basic implementation of a 32-bit signed integer type.

    >>> from tempfile import TemporaryFile
    >>> tmp = TemporaryFile()
    >>> i = CIntBase()
    >>> i.setValue(-1)
    >>> i.getValue()
    -1
    >>> i.setValue(0x11223344)
    >>> i.write(tmp)
    >>> j = CIntBase()
    >>> tmp.seek(0)
    >>> j.read(tmp)
    >>> hex(j.getValue())
    '0x11223344'
    >>> i.setValue(0x10000000000L) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    OverflowError: ...
    >>> i.setValue('hello world')
    Traceback (most recent call last):
        ...
    TypeError: an integer is required
    >>> tmp.seek(0)
    >>> tmp.write('\x11\x22\x33\x44')
    >>> tmp.seek(0)
    >>> i.read(tmp)
    >>> hex(i.getValue())
    '0x44332211'
    """

    cdef int _value

    def __init__(self, **kwargs):
        self._parent = kwargs.get("parent")
        self._value = 0

    def getValue(self):
        """Return stored value."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        self._value = value

    def read(self, stream, **kwargs):
        """Read value from stream."""
        fread(&self._value, 4, 1, PyFile_AsFile(stream))

    def write(self, stream, **kwargs):
        """Write value to stream."""
        fwrite(&self._value, 4, 1, PyFile_AsFile(stream))

    def __str__(self):
        return str(self._value)

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 4

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self._value

    def qDelegateMinimum(self):
        return -2147483648

    def qDelegateMaximum(self):
        return +2147483647

cdef class CUIntBase(CBasicBase):
    """Basic implementation of a 32-bit unsigned integer type."""

    cdef unsigned int _value

    def __init__(self, **kwargs):
        self._parent = kwargs.get("parent")
        self._value = 0

    def getValue(self):
        """Return stored value."""
        # only return a long if the value does not fit in an int
        if self._value <= 2147483647:
            return PyInt_FromLong(self._value)
        else:
            return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        self._value = value

    def read(self, stream, **kwargs):
        """Read value from stream."""
        fread(&self._value, 4, 1, PyFile_AsFile(stream))

    def write(self, stream, **kwargs):
        """Write value to stream."""
        fwrite(&self._value, 4, 1, PyFile_AsFile(stream))

    def __str__(self):
        return str(self._value)

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 4

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self._value

    def qDelegateMinimum(self):
        return 0

    def qDelegateMaximum(self):
        return 4294967295

cdef class CShortBase(CBasicBase):
    """Basic implementation of a 16-bit signed integer type."""

    cdef short _value

    def __init__(self, **kwargs):
        self._parent = kwargs.get("parent")
        self._value = 0

    def getValue(self):
        """Return stored value."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        self._value = value

    def read(self, stream, **kwargs):
        """Read value from stream."""
        fread(&self._value, 2, 1, PyFile_AsFile(stream))

    def write(self, stream, **kwargs):
        """Write value to stream."""
        fwrite(&self._value, 2, 1, PyFile_AsFile(stream))

    def __str__(self):
        return str(self._value)

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 2

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self._value

    def qDelegateMinimum(self):
        return -32768

    def qDelegateMaximum(self):
        return +32767

cdef class CUShortBase(CBasicBase):
    """Basic implementation of a 16-bit unsigned integer type."""

    cdef unsigned short _value

    def __init__(self, **kwargs):
        self._parent = kwargs.get("parent")
        self._value = 0

    def getValue(self):
        """Return stored value."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        self._value = value

    def read(self, stream, **kwargs):
        """Read value from stream."""
        fread(&self._value, 2, 1, PyFile_AsFile(stream))

    def write(self, stream, **kwargs):
        """Write value to stream."""
        fwrite(&self._value, 2, 1, PyFile_AsFile(stream))

    def __str__(self):
        return str(self._value)

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 2

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self._value

    def qDelegateMinimum(self):
        return 0

    def qDelegateMaximum(self):
        return 65535

cdef class CByteBase(CBasicBase):
    """Basic implementation of a 8-bit signed integer type."""

    cdef char _value

    def __init__(self, **kwargs):
        self._parent = kwargs.get("parent")
        self._value = 0

    def getValue(self):
        """Return stored value."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        self._value = value

    def read(self, stream, **kwargs):
        """Read value from stream."""
        fread(&self._value, 1, 1, PyFile_AsFile(stream))

    def write(self, stream, **kwargs):
        """Write value to stream."""
        fwrite(&self._value, 1, 1, PyFile_AsFile(stream))

    def __str__(self):
        return str(self._value)

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 1

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self._value

    def qDelegateMinimum(self):
        return -128

    def qDelegateMaximum(self):
        return +127

cdef class CUByteBase(CBasicBase):
    """Basic implementation of a 8-bit unsigned integer type."""

    cdef unsigned char _value

    def __init__(self, **kwargs):
        self._parent = kwargs.get("parent")
        self._value = 0

    def getValue(self):
        """Return stored value."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        self._value = value

    def read(self, stream, **kwargs):
        """Read value from stream."""
        fread(&self._value, 1, 1, PyFile_AsFile(stream))

    def write(self, stream, **kwargs):
        """Write value to stream."""
        fwrite(&self._value, 1, 1, PyFile_AsFile(stream))

    def __str__(self):
        return str(self._value)

    def getSize(self, **kwargs):
        """Return size of this type."""
        return 1

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self._value

    def qDelegateMinimum(self):
        return 0

    def qDelegateMaximum(self):
        return 255
