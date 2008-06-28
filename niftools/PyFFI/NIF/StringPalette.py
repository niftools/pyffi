"""Custom functions for StringPalette."""

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

def getString(self, offset):
    """Return string at given offset.

    >>> from PyFFI.Formats.NIF import NifFormat
    >>> pal = NifFormat.StringPalette()
    >>> pal.addString("abc")
    0
    >>> pal.addString("def")
    4
    >>> pal.getString(0)
    'abc'
    >>> pal.getString(4)
    'def'
    >>> pal.getString(5) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...
    >>> pal.getString(100) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...
    """
    # check that offset isn't too large
    if offset >= len(self.palette):
        raise ValueError(
            "StringPalette: getting string at %i but palette is only %i long"
            % (offset, len(self.palette)))
    # check that a string starts at this offset
    if offset > 0 and self.palette[offset-1] != "\x00":
        raise ValueError(
            "StringPalette: no string starts at offset %i" % offset)
    # return the string
    return self.palette[offset:self.palette.find("\x00", offset)]

def getAllStrings(self):
    """Return a list of all strings.

    >>> from PyFFI.Formats.NIF import NifFormat
    >>> pal = NifFormat.StringPalette()
    >>> pal.addString("abc")
    0
    >>> pal.addString("def")
    4
    >>> pal.getAllStrings()
    ['abc', 'def']
    >>> pal.palette
    'abc\\x00def\\x00'
    """
    return self.palette[:-1].split("\x00")

def addString(self, text):
    """Adds string to palette (will recycle existing strings if possible) and
    return offset to the string in the palette.

    >>> from PyFFI.Formats.NIF import NifFormat
    >>> pal = NifFormat.StringPalette()
    >>> pal.addString("abc")
    0
    >>> pal.addString("abc")
    0
    >>> pal.addString("def")
    4
    >>> pal.getString(4)
    'def'
    """
    # check if string is already in the palette
    # ... at the start
    if text + '\x00' == self.palette[:len(text) + 1]:
        return 0
    # ... or elsewhere
    offset = self.palette.find('\x00' + text + '\x00')
    if offset != -1:
        return offset + 1
    # if no match, add the string
    if offset == -1:
        offset = len(self.palette)
        self.palette = self.palette + text + "\x00"
        self.length += len(text) + 1
    # return the offset
    return offset
