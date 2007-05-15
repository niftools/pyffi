# --------------------------------------------------------------------------
# NifFormat.BasicTypes
# Implementation of all basic types in the xml NIF file format description.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, NIF File Format Library and Tools.
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

import struct
from FileFormat.Bases.Basic import BasicBase

class Bool(BasicBase):
    _isTemplate = False

    def __init__(self, template = None, argument = None):
        self.setValue(False)

    def getValue(self):
        return self._x

    def setValue(self, value):
        if value:
            self._x = True
        else:
            self._x = False

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        if version > 0x04000002:
            value, = struct.unpack('<B', f.read(1))
        else:
            value, = struct.unpack('<I', f.read(4))
        self._x = bool(value)

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        if version > 0x04000002:
            f.write(struct.pack('<B', int(self._x)))
        else:
            f.write(struct.pack('<I', int(self._x)))

class Int(BasicBase):
    """Basic implementation of a 32-bit signed integer type.

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
    
    _isTemplate = False
    _min = -0x80000000
    _max = 0x7fffffff
    _struct = 'i'
    _size = 4

    def __init__(self, template = None, argument = None):
        self._x = '\x00' * self._size
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
                raise ValueError("cannot convert value '%s' to integer"%str(value))
        if x < self._min or x > self._max:
            raise ValueError('value out of range (%i)'%self.getValue())
        self._x = struct.pack('<' + self._struct, x)

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        # file must be an instance of the type
        self._x = f.read(self._size)

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        f.write(self._x)

    def __str__(self):
        return str(self.getValue())

class UInt(Int):
    _isTemplate = False
    _min = 0
    _max = 0xffffffff
    _struct = 'I'
    _size = 4

class Byte(Int):
    _isTemplate = False
    _min = 0
    _max = 0xff
    _struct = 'B'
    _size = 1

class Char(BasicBase):
    _isTemplate = False
    def __init__(self, template = None, argument = None):
        self.setValue('\x00')

    def getValue(self):
        return self._x

    def setValue(self, value):
        assert(isinstance(value, str))
        assert(len(value) == 1)
        self._x = value

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        self._x = f.read(1)

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        f.write(self._x)

    def __str__(self):
        return self._x

class Short(Int):
    _isTemplate = False
    _min = -0x8000
    _max = 0x7fff
    _struct = 'h'
    _size = 2

class UShort(UInt):
    _isTemplate = False
    _min = 0
    _max = 0xffff
    _struct = 'H'
    _size = 2

class Flags(UShort):
    _isTemplate = False
    def __str__(self):
        return hex(self.getValue())

class Float(BasicBase):
    _isTemplate = False
    def __init__(self, template = None, argument = None):
        self._x = '\x00\x00\x00\x00'
        #self.setValue(0.0)

    def getValue(self):
        return struct.unpack('<f', self._x)[0]

    def setValue(self, value):
        self._x = struct.pack('<f', value)

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        self._x = f.read(4)

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        f.write(self._x)

class Ref(BasicBase):
    _isTemplate = True
    _hasLinks = True
    _hasRefs = True
    def __init__(self, template = None, argument = None):
        self._template = template
        self.setValue(None)

    def getValue(self):
        return self._x

    def setValue(self, value):
        if value == None:
            self._x = None
        else:
            if not isinstance(value, self._template):
                raise TypeError('expected an instance of %s but got instance of %s'%(self._template, value.__class__))
            self._x = value

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        self._x = None # fixLinks will set this field
        block_index, = struct.unpack('<i', f.read(4))
        link_stack.append(block_index)

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        if self._x == None: # link by block number
            if version >= 0x0303000D:
                f.write('\xff\xff\xff\xff') # link by number
            else:
                f.write('\x00\x00\x00\x00') # link by pointer
        else:
            f.write(struct.pack('<i', block_index_dct[self._x]))

    def fixLinks(self, version, user_version, block_dct, link_stack):
        block_index = link_stack.pop(0)
        # case when there's no link
        if version >= 0x0303000D:
            if block_index == -1: # link by block number
                self._x = None
                return
        else:
            if block_index == 0: # link by pointer
                self._x = None
                return
        # other case: look up the link and check the link type
        block = block_dct[block_index]
        if not isinstance(block, self._template):
            raise TypeError('expected an instance of %s but got instance of %s'%(self._template, block.__class__))
        self._x = block

    def getLinks(self, version, user_version):
        if self._x != None:
            return [self._x]
        else:
            return []

    def getRefs(self, version, user_version):
        if self._x != None:
            return [self._x]
        else:
            return []

class Ptr(Ref):
    _isTemplate = True
    _hasLinks = True
    _hasRefs = False
    
    def __str__(self):
        # avoid infinite recursion
        return '%s instance at 0x%08X'%(self._x.__class__, id(self._x))

    def getRefs(self, version, user_version):
        return []

class LineString(BasicBase):
    """Basic type for strings ending in a newline character (0x0a).

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> l = LineString()
    >>> f.write('abcdefg\\x0a')
    >>> f.seek(0)
    >>> l.read(f = f)
    >>> str(l)
    'abcdefg'
    >>> f.seek(0)
    >>> l.setValue('Hi There')
    >>> l.write(f = f)
    >>> f.seek(0)
    >>> m = LineString()
    >>> m.read(f = f)
    >>> str(m)
    'Hi There'
    """
    _isTemplate = False
    def __init__(self, template = None, argument = None):
        self.setValue('')

    def getValue(self):
        return self._x

    def setValue(self, value):
        self._x = str(value).rstrip('\x0a')

    def __str__(self):
        s = BasicBase.__str__(self)
        if not s: return '<EMPTY STRING>'
        return s

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        self._x = f.readline().rstrip('\x0a')

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        f.write("%s\x0a"%self._x)

class HeaderString(BasicBase):
    _isTemplate = False
    
    def __init__(self, template = None, argument = None):
        pass

    def __str__(self):
        return 'NetImmerse/Gamebryo File Format, Version x.x.x.x'

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        version_string = self.versionString(version)
        s = f.read(len(version_string) + 1)
        if s != version_string + '\x0a':
            raise ValueError("invalid NIF header: expected '%s' but got '%s'"%(version_string, s[:-1]))

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        f.write(self.versionString(version) + '\x0a')

    @staticmethod
    def versionString(version):
        """Transforms version number into a version string.

        >>> HeaderString.versionString(0x03010000)
        'NetImmerse File Format, Version 3.1'
        >>> HeaderString.versionString(0x0A000100)
        'NetImmerse File Format, Version 10.0.1.0'
        >>> HeaderString.versionString(0x0A010000)
        'Gamebryo File Format, Version 10.1.0.0'
        """
        if version <= 0x0A000102:
            s = "NetImmerse"
        else:
            s = "Gamebryo"
        if version <= 0x03010000:
            v = "%i.%i"%((version >> 24) & 0xff, (version >> 16) & 0xff)
        else:
            v = "%i.%i.%i.%i"%((version >> 24) & 0xff, (version >> 16) & 0xff, (version >> 8) & 0xff, version & 0xff)
        return "%s File Format, Version %s"%(s, v)

class FileVersion(BasicBase):
    _isTemplate = False

    def __init__(self, template = None, argument = None):
        pass

    def getValue(self):
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplementedError

    def __str__(self):
        return 'x.x.x.x'

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        ver, = struct.unpack('<I', f.read(4))
        if ver != version:
            raise ValueError('invalid version number: expected 0x%08X but got 0x%08X'%(version, ver))

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        f.write(struct.pack('<I', version))

class String(BasicBase):
    """Basic type for strings.

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> s = String()
    >>> f.write('\\x07\\x00\\x00\\x00abcdefg')
    >>> f.seek(0)
    >>> s.read(f = f)
    >>> str(s)
    'abcdefg'
    >>> f.seek(0)
    >>> s.setValue('Hi There')
    >>> s.write(f = f)
    >>> f.seek(0)
    >>> m = String()
    >>> m.read(f = f)
    >>> str(m)
    'Hi There'
    """
    _isTemplate = False
    def __init__(self, template = None, argument = None):
        self.setValue('')

    def getValue(self):
        return self._x

    def setValue(self, value):
        if len(value) > 10000: raise ValueError('string too long')
        self._x = str(value)

    def __str__(self):
        s = self._x
        if not s: return '<EMPTY STRING>'
        return s

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        n, = struct.unpack('<I', f.read(4))
        if n > 10000: raise ValueError('string too long (0x%08X at 0x%08X)'%(n, f.tell()))
        self._x = f.read(n)

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        f.write(struct.pack('<I', len(self._x)))
        f.write(self._x)

class ShortString(BasicBase):
    """Another type for strings."""
    _isTemplate = False
    def __init__(self, template = None, argument = None):
        self._x = ''

    def getValue(self):
        return self._x

    def setValue(self, value):
        if len(value) > 254: raise ValueError('string too long')
        self._x = str(value)

    def __str__(self):
        s = self._x
        if not s: return '<EMPTY STRING>'
        return s

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        n, = struct.unpack('<B', f.read(1))
        self._x = f.read(n).rstrip('\x00')

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        f.write(struct.pack('<B', len(self._x)+1))
        f.write(self._x + '\x00')
