"""Abstract base class for simple types."""

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

from PyFFI.ObjectModels.Tree import DetailTreeLeaf

# derives from DetailTreeLeaf because simple types can be displayed in the
# detail view, as leafs of the display tree
class SimpleType(DetailTreeLeaf):
    """Abstract base class from which all simple types are derived. Simple
    types contain data which is not divided further into smaller bits.

    >>> import struct
    >>> class UInt(SimpleType):
    ...     def __init__(self, **kwargs):
    ...         self.__value = 0
    ...     def read(self, stream, **kwargs):
    ...         self.__value, = struct.unpack('<I', stream.read(4))
    ...     def write(self, stream, **kwargs):
    ...         stream.write(struct.pack('<I', self.__value))
    ...     def getValue(self):
    ...         return self.__value
    ...     def setValue(self, value):
    ...         self.__value = int(value)
    >>> x = UInt()
    >>> x.setValue('123')
    >>> x.getValue()
    123
    """

    def read(self, stream, **kwargs):
        """Read object from file.

        @param stream: The stream to read from.
        @type stream: file
        """
        raise NotImplementedError

    def write(self, stream, **kwargs):
        """Write object to file.

        @param stream: The stream to write to.
        @type stream: file
        """
        raise NotImplementedError

    def getValue(self):
        """Return object value.

        @return: Object value.
        """
        raise NotImplementedError

    def setValue(self, value):
        """Set object value.

        @param value: The new object value.
        @type value: any (whatever is suitable for the implemented type)
        """
        raise NotImplementedError

    def getHash(self, **kwargs):
        """Returns a hash value (an immutable object) that can be used to
        identify the object uniquely.

        @return: An immutable object.
        """
        raise NotImplementedError

