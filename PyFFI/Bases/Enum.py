"""Abstract base class for implementing xml enum types."""

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
# ***** END LICENCE BLOCK *****

import struct

from PyFFI.Bases.Basic import BasicBase
from PyFFI.Bases.Delegate import DelegateComboBox

class _MetaEnumBase(type):
    """This metaclass checks for the presence of a _enumitems, _enumvalues,
    and _numbytes attributes. It also adds enum class attributes.

    Used as metaclass of EnumBase."""
    def __init__(cls, name, bases, dct):
        super(_MetaEnumBase, cls).__init__(name, bases, dct)
        # consistency checks
        if not '_enumitems' in dct:
            raise TypeError('%s: missing _enumitems attribute'%cls)
        if not '_enumvalues' in dct:
            raise TypeError('%s: missing _enumvalues attribute'%cls)
        if not '_numbytes' in dct:
            raise TypeError('%s: missing _numbytes attribute'%cls)

        # check storage type
        if cls._numbytes == 1:
            cls._struct = '<B'
        elif cls._numbytes == 2:
            cls._struct = '<H'
        elif cls._numbytes == 4:
            cls._struct = '<I'
        else:
            raise RuntimeError("unsupported enum numbytes")

        # template type?
        cls._isTemplate = False
        # does the type contain a Ref or a Ptr?
        cls._hasLinks = False
        # does the type contain a Ref?
        cls._hasRefs = False
        # does the type contain a string?
        cls._hasStrings = False

        # for other read/write checking
        cls._min = 0
        cls._max = (1 << (cls._numbytes * 8)) - 1

        # set enum values as class attributes
        for item, value in zip(cls._enumitems, cls._enumvalues):
            setattr(cls, item, value)

class EnumBase(BasicBase,DelegateComboBox):
    __metaclass__ = _MetaEnumBase
    _enumitems = []
    _enumvalues = []
    _numbytes = 1 # default width of an enum

    #
    # BasicBase methods
    #

    def __init__(self, **kwargs):
        super(EnumBase, self).__init__(**kwargs)
        self._value = 0

    def getValue(self):
        """Return stored value."""
        return self._value

    def setValue(self, value):
        """Set value to C{value}."""
        try:
            val = int(value)
        except ValueError:
            try:
                val = int(value, 16) # for '0x...' strings
            except ValueError:
                if value in self._enumitems:
                    val = getattr(self, value)
                else:
                    raise ValueError(
                        "cannot convert value '%s' to integer"%value)
        if not val in self._enumvalues:
            raise ValueError('invalid enum value (%i)' % val)
        self._value = val

    def read(self, stream, **kwargs):
        """Read value from stream."""
        self._value = struct.unpack(self._struct, stream.read(self._numbytes))[0]

    def write(self, stream, **kwargs):
        """Write value to stream."""
        stream.write(struct.pack(self._struct, self._value))

    def __str__(self):
        try:
            return self._enumitems[self._enumvalues.index(self.getValue())]
        except ValueError:
            # not in _enumvalues list
            return "<INVALID (%i)>" % self.getValue()

    def getSize(self, **kwargs):
        """Return size of this type."""
        return self._numbytes

    def getHash(self, **kwargs):
        """Return a hash value for this value."""
        return self.getValue()

    #
    # DelegateComboBox methods
    #

    def qDelegateKeys(self):
        """List or tuple of strings, each string describing an item."""
        return self._enumitems

    def qDelegateValue(self, index):
        """List or tuple of strings, each string describing an item."""
        return self._enumvalues[index]

    def qDelegateIndex(self):
        """Get the value of an item string."""
        return self._enumvalues.index(self._value)

    def qDataDisplay(self):
        """Return object that can be used to display the instance."""
        try:
            return self._enumitems[self._enumvalues.index(self._value)]
        except ValueError:
            # value self._value is not in the self._enumvalues list
            return "<INVALID (0x%08X)>" % self._value
