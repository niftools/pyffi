# --------------------------------------------------------------------------
# PyFFI.Bases.Basic
# Implements class for basic types (xml tag <basic>).
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, Python File Format Interface
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
# --------------------------------------------------------------------------

class BasicBase(object):
    """Base class from which all basic types are derived.
    
    The BasicBase class implements the interface for basic types.
    All basic types are derived from this class.
    They must override read, write, getValue, and setValue.

    >>> import struct
    >>> class UInt(BasicBase):
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
    >>> class Test(BasicBase): # bad: read, write, getValue, and setValue are not implemented
    ...     pass
    >>> x = Test() # doctest: +ELLIPSIS
    >>> x.setValue('123') # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    NotImplementedError
    """
    
    _isTemplate = False # is it a template type?
    _hasLinks = False # does the type contain a Ref or a Ptr?
    _hasRefs = False # does the type contain a Ref?
    _hasStrings = False # does the type contain a string?
    
    def __init__(self, template = None, argument = None):
        """Initializes the instance.

        @param template: type used as template
        @param argument: argument used to initialize the instance (see the Struct class)"""
        pass

    # string representation
    def __str__(self):
        """Return string representation."""
        return str(self.getValue())

    def read(self, **kwargs):
        """Read object from file."""
        raise NotImplementedError

    def write(self, **kwargs):
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

    def getSize(self, **kwargs):
        """Returns size of the object in bytes."""
        raise NotImplementedError

    def getHash(self, **kwargs):
        """Returns a hash value (an immutable object) that can be used to
        identify the object uniquely."""
        raise NotImplementedError

