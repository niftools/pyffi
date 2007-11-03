"""
This module implements the NIF file format.

Examples
========

Read a NIF file
---------------

>>> # get version and user version, and read nif file
>>> f = open('test.nif', 'rb')
>>> version, user_version = NifFormat.getVersion(f)
>>> if version == -1:
...     raise RuntimeError('nif version not supported')
... elif version == -2:
...     raise RuntimeError('not a nif file')
>>> roots = NifFormat.read(f, version = version, user_version = user_version)
>>> # print all NiNode names
>>> for root in roots:
...     for block in root.tree():
...         if isinstance(block, NifFormat.NiNode):
...             print block.name
test

Create a NIF model from scratch and write to file
-------------------------------------------------

>>> root = NifFormat.NiNode()
>>> root.name = 'Scene Root'
>>> blk = NifFormat.NiNode()
>>> root.addChild(blk)
>>> blk.name = 'new block'
>>> blk.scale = 2.4
>>> blk.translation.x = 3.9
>>> blk.rotation.m11 = 1.0
>>> blk.rotation.m22 = 1.0
>>> blk.rotation.m33 = 1.0
>>> ctrl = NifFormat.NiVisController()
>>> ctrl.flags = 0x000c
>>> ctrl.target = blk
>>> blk.addController(ctrl)
>>> blk.addController(NifFormat.NiAlphaController())
>>> strips = NifFormat.NiTriStrips()
>>> root.addChild(strips, front = True)
>>> strips.name = "hello world"
>>> strips.rotation.m11 = 1.0
>>> strips.rotation.m22 = 1.0
>>> strips.rotation.m33 = 1.0
>>> data = NifFormat.NiTriStripsData()
>>> strips.data = data
>>> data.numVertices = 5
>>> data.hasVertices = True
>>> data.vertices.updateSize()
>>> for i, v in enumerate(data.vertices):
...     v.x = 1.0+i/10.0
...     v.y = 0.2+1.0/(i+1)
...     v.z = 0.03
>>> data.updateCenterRadius()
>>> data.numStrips = 2
>>> data.stripLengths.updateSize()
>>> data.stripLengths[0] = 3
>>> data.stripLengths[1] = 4
>>> data.hasPoints = True
>>> data.points.updateSize()
>>> data.points[0][0] = 0
>>> data.points[0][1] = 1
>>> data.points[0][2] = 2
>>> data.points[1][0] = 1
>>> data.points[1][1] = 2
>>> data.points[1][2] = 3
>>> data.points[1][3] = 4
>>> data.numUvSets = 1
>>> data.hasUv = True
>>> data.uvSets.updateSize()
>>> for i, v in enumerate(data.uvSets[0]):
...     v.u = 1.0-i/10.0
...     v.v = 1.0/(i+1)
>>> data.hasNormals = True
>>> data.normals.updateSize()
>>> for i, v in enumerate(data.normals):
...     v.x = 0.0
...     v.y = 0.0
...     v.z = 1.0
>>> strips.updateTangentSpace()
>>> from tempfile import TemporaryFile
>>> f = TemporaryFile()
>>> NifFormat.write(f, version = 0x14010003, user_version = 10, roots = [root])

Get list of versions and games
------------------------------

>>> for vnum in sorted(NifFormat.versions.values()): print '0x%08X'%vnum
0x03000000
0x03000300
0x03010000
0x0303000D
0x04000000
0x04000002
0x0401000C
0x04020002
0x04020100
0x04020200
0x0A000100
0x0A000102
0x0A000103
0x0A010000
0x0A01006A
0x0A020000
0x14000004
0x14000005
0x14010003
0x14020007
0x14020008
0x14030003
0x14030006
0x14030009
>>> for game, versions in sorted(NifFormat.games.items(), key=lambda x: x[0]):
...     print game,
...     for vnum in versions:
...         print '0x%08X'%vnum,
...     print
? 0x0A000103
Axis and Allies 0x0A010000
Civilization IV 0x04020002 0x04020100 0x04020200 0x0A000100 0x0A010000 0x0A020000 0x14000004
Dark Age of Camelot 0x03000300 0x03010000 0x0401000C 0x04020100 0x04020200 0x0A010000
Emerge 0x14020007 0x14020008 0x14030003 0x14030006
Empire Earth II 0x04020200
Entropia Universe 0x0A010000
Freedom Force 0x04000000 0x04000002
Freedom Force vs. the 3rd Reich 0x0A010000
Kohan 2 0x0A010000
Loki 0x0A020000
Megami Tensei: Imagine 0x14010003
Morrowind 0x04000002
Oblivion 0x0303000D 0x0A000102 0x0A01006A 0x0A020000 0x14000004 0x14000005
Prison Tycoon 0x0A020000
Pro Cycling Manager 0x0A020000
Red Ocean 0x0A020000
Star Trek: Bridge Commander 0x03000000 0x03010000
Warhammer 0x14030009
Zoo Tycoon 2 0x0A000100
>>> print NifFormat.HeaderString
<class 'PyFFI.NIF.HeaderString'>

Some Doctests
=============

These tests are used to check for functionality and bugs in the library.
They also provide code examples which you may find useful.

Reading an unsupported nif file
-------------------------------

>>> f = open('invalid.nif', 'rb')
>>> version, user_version = NifFormat.getVersion(f)
>>> if version == -1:
...     raise RuntimeError('nif version not supported')
... elif version == -2:
...     raise RuntimeError('not a nif file')
>>> roots = NifFormat.read(f, version = version, user_version = user_version) # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
NifError: ...

Template Types
--------------

>>> block = NifFormat.NiTextKeyExtraData()
>>> block.numTextKeys = 1
>>> block.textKeys.updateSize()
>>> block.textKeys[0].time = 1.0
>>> block.textKeys[0].value = 'hi'

Links
-----

>>> NifFormat.NiNode._hasLinks
True
>>> NifFormat.NiBone._hasLinks
True
>>> skelroot = NifFormat.NiNode()
>>> geom = NifFormat.NiTriShape()
>>> geom.skinInstance = NifFormat.NiSkinInstance()
>>> geom.skinInstance.skeletonRoot = skelroot
>>> [ block.__class__.__name__ for block in geom.getRefs() ]
['NiSkinInstance']
>>> [ block.__class__.__name__ for block in geom.getLinks() ]
['NiSkinInstance']
>>> [ block.__class__.__name__ for block in geom.skinInstance.getRefs() ]
[]
>>> [ block.__class__.__name__ for block in geom.skinInstance.getLinks() ]
['NiNode']

Mathematics
-----------

>>> m = NifFormat.Matrix44()
>>> m.setIdentity()
>>> print m
[  1.000  0.000  0.000  0.000 ]
[  0.000  1.000  0.000  0.000 ]
[  0.000  0.000  1.000  0.000 ]
[  0.000  0.000  0.000  1.000 ]
<BLANKLINE>
>>> s, r, t = m.getScaleRotationTranslation()
>>> print s
1.0
>>> print r
[  1.000  0.000  0.000 ]
[  0.000  1.000  0.000 ]
[  0.000  0.000  1.000 ]
<BLANKLINE>
>>> print t
[  0.000  0.000  0.000 ]
>>> m.getMatrix33().isScaleRotation()
True
>>> m.m21 = 2.0
>>> m.getMatrix33().isScaleRotation()
False
>>> m = NifFormat.Matrix33()
>>> m.m11 = -0.434308
>>> m.m12 =  0.893095
>>> m.m13 = -0.117294
>>> m.m21 = -0.451770
>>> m.m22 = -0.103314
>>> m.m23 =  0.886132
>>> m.m31 =  0.779282
>>> m.m32 =  0.437844
>>> m.m33 =  0.448343
>>> m == m
True
>>> m != m
False
>>> print "%.4f"%m.getDeterminant()
1.0000
>>> m.isRotation()
True
>>> print m.getTranspose()
[ -0.434 -0.452  0.779 ]
[  0.893 -0.103  0.438 ]
[ -0.117  0.886  0.448 ]
<BLANKLINE>
>>> m.getInverse() == m.getTranspose()
True
>>> m *= 0.321
>>> print "%.5f"%m.getScale()
0.32100
>>> s, r = m.getInverse().getScaleRotation()
>>> print "%.5f"%s
3.11526
>>> abs(0.321 - 1/s) < NifFormat._EPSILON
True
>>> print r # same as print m.getTranspose() above
[ -0.434 -0.452  0.779 ]
[  0.893 -0.103  0.438 ]
[ -0.117  0.886  0.448 ]
<BLANKLINE>
>>> abs(m.getDeterminant() - 0.321 ** 3) < NifFormat._EPSILON
True
>>> m *= -2
>>> print m
[  0.279 -0.573  0.075 ]
[  0.290  0.066 -0.569 ]
[ -0.500 -0.281 -0.288 ]
<BLANKLINE>
>>> print "%.5f"%m.getScale()
-0.64200
>>> abs(m.getDeterminant() + 0.642 ** 3) < NifFormat._EPSILON
True
>>> n = NifFormat.Matrix44()
>>> n.setIdentity()
>>> n.setMatrix33(m)
>>> t = NifFormat.Vector3()
>>> t.x = 1.2
>>> t.y = 3.4
>>> t.z = 5.6
>>> n.setTranslation(t)
>>> print n
[  0.279 -0.573  0.075  0.000 ]
[  0.290  0.066 -0.569  0.000 ]
[ -0.500 -0.281 -0.288  0.000 ]
[  1.200  3.400  5.600  1.000 ]
<BLANKLINE>
>>> n == n
True
>>> n != n
False
>>> print n.getInverse()
[  0.676  0.704 -1.214  0.000 ]
[ -1.391  0.161 -0.682  0.000 ]
[  0.183 -1.380 -0.698  0.000 ]
[  2.895  6.338  7.686  1.000 ]
<BLANKLINE>
>>> print n.getInverse(fast = False) + 0.000001 # workaround for -0.000
[  0.676  0.704 -1.214  0.000 ]
[ -1.391  0.161 -0.682  0.000 ]
[  0.183 -1.380 -0.698  0.000 ]
[  2.895  6.338  7.686  1.000 ]
<BLANKLINE>
>>> (n * n.getInverse()).isIdentity()
True
"""

# --------------------------------------------------------------------------
# PyFFI.NIF
# Implementation of the NIF file format; uses PyFFI.
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

import struct, os, re

from PyFFI import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI import Common
from PyFFI.Bases.Basic import BasicBase

class NifFormat(object):
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'nif.xml'
    xmlFilePath = [ os.getenv('NIFXMLPATH'), os.path.dirname(__file__) ] # where to look for nif.xml and in what order: NIFXMLPATH env var, or NifFormat module directory
    clsFilePath = os.path.dirname(__file__) # path of class customizers
    _EPSILON = 0.0001 # used for comparing floats
    
    # basic types
    int = Common.Int
    uint = Common.UInt
    byte = Common.UByte # not a typo
    char = Common.Char
    short = Common.Short
    ushort = Common.UShort
    float = Common.Float
    BlockTypeIndex = Common.UShort
    StringOffset = Common.UInt
    StringIndex = Common.UInt



    # implementation of nif-specific basic types

    class bool(BasicBase):
        """Basic implementation of a 32-bit (8-bit for versions > 4.0.0.2)
        boolean type.
        
        >>> i = NifFormat.bool()
        >>> i.setValue('false')
        >>> i.getValue()
        False
        >>> i.setValue('true')
        >>> i.getValue()
        True
        """
        def __init__(self, **kwargs):
            self.setValue(False)

        def getValue(self):
            return self._value

        def setValue(self, value):
            if isinstance(value, basestring):
                if value.lower() == 'false':
                    self._value = False
                    return
                elif value == '0':
                    self._value = False
                    return
            if value:
                self._value = True
            else:
                self._value = False

        def getSize(self, **kwargs):
            if kwargs.get('version', -1) > 0x04000002:
                return 1
            else:
                return 4

        def getHash(self, **kwargs):
            return self._value

        def read(self, stream, **kwargs):
            if kwargs.get('version', -1) > 0x04000002:
                value, = struct.unpack('<B', stream.read(1))
            else:
                value, = struct.unpack('<I', stream.read(4))
            self._value = bool(value)

        def write(self, stream, **kwargs):
            if kwargs.get('version', -1) > 0x04000002:
                stream.write(struct.pack('<B', int(self._value)))
            else:
                stream.write(struct.pack('<I', int(self._value)))

    class Flags(Common.UShort):
        def __str__(self):
            return hex(self.getValue())

    class Ref(BasicBase):
        """Reference to another block."""
        _isTemplate = True
        _hasLinks = True
        _hasRefs = True
        def __init__(self, template = None, **kwargs):
            self._template = template
            self.setValue(None)

        def getValue(self):
            return self._value

        def setValue(self, value):
            if value == None:
                self._value = None
            else:
                if not isinstance(value, self._template):
                    raise TypeError('expected an instance of %s but got instance of %s'%(self._template, value.__class__))
                self._value = value

        def getSize(self, **kwargs):
            return 4

        def getHash(self, **kwargs):
            if self._value: return self._value.getHash(**kwargs)
            else: return None

        def read(self, stream, **kwargs):
            self._value = None # fixLinks will set this field
            block_index, = struct.unpack('<i', stream.read(4))
            kwargs.get('link_stack', []).append(block_index)

        def write(self, stream, **kwargs):
            """Write block reference.

            @param block_index_dct: The dictionary of block indices
                (block -> index).
            """
            if self._value == None: # link by block number
                if kwargs.get('version', -1) >= 0x0303000D:
                    stream.write('\xff\xff\xff\xff') # link by number
                else:
                    stream.write('\x00\x00\x00\x00') # link by pointer
            else:
                stream.write(struct.pack(
                    '<i', kwargs.get('block_index_dct')[self._value]))

        def fixLinks(self, **kwargs):
            """Fix block links.

            @param link_stack: The link stack.
            @param block_dct: The block dictionary (index -> block).
            """
            block_index = kwargs.get('link_stack').pop(0)
            # case when there's no link
            if kwargs.get('version', -1) >= 0x0303000D:
                if block_index == -1: # link by block number
                    self._value = None
                    return
            else:
                if block_index == 0: # link by pointer
                    self._value = None
                    return
            # other case: look up the link and check the link type
            block = kwargs.get('block_dct')[block_index]
            if not isinstance(block, self._template):
                raise TypeError('expected an instance of %s but got instance of %s'%(self._template, block.__class__))
            self._value = block

        def getLinks(self, **kwargs):
            if self._value != None:
                return [self._value]
            else:
                return []

        def getRefs(self, **kwargs):
            if self._value != None:
                return [self._value]
            else:
                return []

    class Ptr(Ref):
        """A weak reference to another block, used to point up the hierarchy tree. The reference is not returned by the L{getRefs} function to avoid infinite recursion."""
        _isTemplate = True
        _hasLinks = True
        _hasRefs = False
        
        def __str__(self):
            # avoid infinite recursion
            return '%s instance at 0x%08X'%(self._value.__class__, id(self._value))

        def getRefs(self, **kwargs):
            return []

        def getHash(self, **kwargs):
            return None

    class LineString(BasicBase):
        """Basic type for strings ending in a newline character (0x0a).

        >>> from tempfile import TemporaryFile
        >>> f = TemporaryFile()
        >>> l = NifFormat.LineString()
        >>> f.write('abcdefg\\x0a')
        >>> f.seek(0)
        >>> l.read(f)
        >>> str(l)
        'abcdefg'
        >>> f.seek(0)
        >>> l.setValue('Hi There')
        >>> l.write(f)
        >>> f.seek(0)
        >>> m = NifFormat.LineString()
        >>> m.read(f)
        >>> str(m)
        'Hi There'
        """
        def __init__(self, template = None, argument = None):
            self.setValue('')

        def getValue(self):
            return self._value

        def setValue(self, value):
            self._value = str(value).rstrip('\x0a')

        def __str__(self):
            s = BasicBase.__str__(self)
            if not s: return '<EMPTY STRING>'
            return s

        def getSize(self, **kwargs):
            return len(self._value) + 1 # +1 for trailing endline

        def getHash(self, **kwargs):
            return self.getValue()

        def read(self, stream, **kwargs):
            self._value = stream.readline().rstrip('\x0a')

        def write(self, stream, **kwargs):
            stream.write("%s\x0a"%self._value)

    class HeaderString(BasicBase):
        def __init__(self, **kwargs):
            pass

        def __str__(self):
            return 'NetImmerse/Gamebryo File Format, Version x.x.x.x'

        def getHash(self, **kwargs):
            return None

        def read(self, stream, **kwargs):
            version_string = self.versionString(kwargs.get('version'))
            s = stream.read(len(version_string) + 1)
            if s != version_string + '\x0a':
                raise ValueError("invalid NIF header: expected '%s' but got '%s'"%(version_string, s[:-1]))

        def write(self, stream, **kwargs):
            stream.write(self.versionString(kwargs.get('version')) + '\x0a')

        def getSize(self, **kwargs):
            return len(self.versionString(kwargs.get('version'))) + 1

        @staticmethod
        def versionString(version):
            """Transforms version number into a version string.

            >>> NifFormat.HeaderString.versionString(0x03000300)
            'NetImmerse File Format, Version 3.03'
            >>> NifFormat.HeaderString.versionString(0x03010000)
            'NetImmerse File Format, Version 3.1'
            >>> NifFormat.HeaderString.versionString(0x0A000100)
            'NetImmerse File Format, Version 10.0.1.0'
            >>> NifFormat.HeaderString.versionString(0x0A010000)
            'Gamebryo File Format, Version 10.1.0.0'
            """
            if version == -1 or version is None:
                raise NifError('no string for version %s'%version)
            if version <= 0x0A000102:
                s = "NetImmerse"
            else:
                s = "Gamebryo"
            if version == 0x03000300:
                v = "3.03"
            elif version <= 0x03010000:
                v = "%i.%i"%((version >> 24) & 0xff, (version >> 16) & 0xff)
            else:
                v = "%i.%i.%i.%i"%((version >> 24) & 0xff, (version >> 16) & 0xff, (version >> 8) & 0xff, version & 0xff)
            return "%s File Format, Version %s"%(s, v)

    class FileVersion(BasicBase):
        def __init__(self, **kwargs):
            pass

        def getValue(self):
            raise NotImplementedError

        def setValue(self, value):
            raise NotImplementedError

        def __str__(self):
            return 'x.x.x.x'

        def getSize(self, **kwargs):
            return 4

        def getHash(self, **kwargs):
            return None

        def read(self, stream, **kwargs):
            ver, = struct.unpack('<I', stream.read(4))
            if ver != kwargs.get('version'):
                raise ValueError('invalid version number: expected 0x%08X but got 0x%08X'%(version, ver))

        def write(self, stream, **kwargs):
            stream.write(struct.pack('<I', kwargs.get('version')))

    class SizedString(BasicBase):
        """Basic type for strings.

        >>> from tempfile import TemporaryFile
        >>> f = TemporaryFile()
        >>> s = NifFormat.SizedString()
        >>> f.write('\\x07\\x00\\x00\\x00abcdefg')
        >>> f.seek(0)
        >>> s.read(f)
        >>> str(s)
        'abcdefg'
        >>> f.seek(0)
        >>> s.setValue('Hi There')
        >>> s.write(f)
        >>> f.seek(0)
        >>> m = NifFormat.SizedString()
        >>> m.read(f)
        >>> str(m)
        'Hi There'
        """
        def __init__(self, **kwargs):
            self.setValue('')

        def getValue(self):
            return self._value

        def setValue(self, value):
            if len(value) > 10000: raise ValueError('string too long')
            self._value = str(value)

        def __str__(self):
            s = self._value
            if not s: return '<EMPTY STRING>'
            return s

        def getSize(self, **kwargs):
            return 4+len(self._value)

        def getHash(self, **kwargs):
            return self.getValue()

        def read(self, stream, **kwargs):
            n, = struct.unpack('<I', stream.read(4))
            if n > 10000: raise ValueError('string too long (0x%08X at 0x%08X)'%(n, stream.tell()))
            self._value = stream.read(n)

        def write(self, stream, **kwargs):
            stream.write(struct.pack('<I', len(self._value)))
            stream.write(self._value)

    class ShortString(BasicBase):
        """Another type for strings."""
        def __init__(self, **kwargs):
            self._value = ''

        def getValue(self):
            return self._value

        def setValue(self, value):
            if len(value) > 254: raise ValueError('string too long')
            self._value = str(value)

        def __str__(self):
            return self._value

        def getHash(self, **kwargs):
            return self.getValue()

        def read(self, stream, **kwargs):
            n, = struct.unpack('<B', stream.read(1))
            self._value = stream.read(n).rstrip('\x00')

        def write(self, stream, **kwargs):
            stream.write(struct.pack('<B', len(self._value)+1))
            stream.write(self._value + '\x00')

    class string(SizedString):
        _hasStrings = True

        def getSize(self, **kwargs):
            if kwargs.get('version', -1) >= 0x14010003:
                return 4
            else:
                return 4+len(self._value)

        def read(self, stream, **kwargs):
            n, = struct.unpack('<i', stream.read(4))
            if kwargs.get('version') >= 0x14010003:
                if n == -1:
                    self._value = ''
                else:
                    try:
                        self._value = kwargs.get('string_list')[n]
                    except IndexError:
                        raise ValueError('string index too large (%i)'%n)
            else:
                if n > 10000: raise ValueError('string too long (0x%08X at 0x%08X)'%(n, stream.tell()))
                self._value = stream.read(n)

        def write(self, stream, **kwargs):
            if kwargs.get('version') >= 0x14010003:
                if self._value == '':
                    stream.write(struct.pack('<i', -1))
                else:
                    try:
                        stream.write(struct.pack(
                            '<i', kwargs.get('string_list').index(self._value)))
                    except ValueError:
                        raise ValueError(
                            "string '%s' not in string list"%self._value)
            else:
                stream.write(struct.pack('<I', len(self._value)))
                stream.write(self._value)

        def getStrings(self, **kwargs):
            if self._value != '':
                return [self._value]
            else:
                return []

        def getHash(self, **kwargs):
            if not kwargs.get('ignore_strings'):
                return self.getValue()

    # other types with internal implementation
    class FilePath(string):
        def getHash(self, **kwargs):
            # never ignore file paths
            # transform to lower case to make hash case insensitive
            return self.getValue().lower()

    # exceptions
    class NifError(StandardError):
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        >>> hex(NifFormat.versionNumber('3.14.15.29'))
        '0x30e0f1d'
        >>> hex(NifFormat.versionNumber('1.2'))
        '0x1020000'
        >>> hex(NifFormat.versionNumber('3.03'))
        '0x3000300'
        """
        
        if version_str == '3.03': return 0x03000300 # 3.03 case is special

        try:
            ver_list = [int(x) for x in version_str.split('.')]
        except ValueError:
            return -1 # version not supported (i.e. version_str '10.0.1.3a' would trigger this)
        if len(ver_list) > 4 or len(ver_list) < 1:
            return -1 # version not supported
        for ver_digit in ver_list:
            if (ver_digit | 0xff) > 0xff:
                return -1 # version not supported
        while len(ver_list) < 4: ver_list.append(0)
        return (ver_list[0] << 24) + (ver_list[1] << 16) + (ver_list[2] << 8) + ver_list[3]

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable by python.

        >>> NifFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """
        
        parts = str(name).replace("?", "X").split() # str(name) converts name to string in case name is a unicode string
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    @classmethod
    def getVersion(cls, stream):
        """Returns version and user version number, if version is supported.
        Returns -1, 0 if version is not supported.
        Returns -2, 0 if <stream> is not a nif file.
        """
        pos = stream.tell()
        try:
            s = stream.readline(64).rstrip()
        finally:
            stream.seek(pos)
        if s.startswith("NetImmerse File Format, Version " ):
            version_str = s[32:]
        elif s.startswith("Gamebryo File Format, Version "):
            version_str = s[30:]
        else:
            return -2, 0 # not a nif file
        try:
            ver = cls.versionNumber(version_str)
        except:
            return -1, 0 # version not supported
        if not ver in cls.versions.values():
            return -1, 0 # unsupported version
        # check version integer and user version
        userver = 0
        if ver >= 0x0303000D:
            ver_int = None
            try:
                stream.readline(64)
                ver_int, = struct.unpack('<I', stream.read(4))
                if ver_int != ver:
                    return -2, 0 # not a nif file
                if ver >= 0x14000004: stream.read(1)
                if ver >= 0x0A010000: userver, = struct.unpack('<I', stream.read(4))
            finally:
                stream.seek(pos)
        return ver, userver

    @classmethod
    def read(cls, stream, version = None, user_version = None, verbose = 0):
        # read header
        if verbose >= 1:
            print "reading block at 0x%08X..."%stream.tell()
        hdr = cls.Header()
        hdr.read(stream, version = version, user_version = user_version)
        if verbose >= 2:
            print hdr

        # read the blocks
        link_stack = [] # list of indices, as they are added to the stack
        string_list = [ str(s) for s in hdr.strings ]
        block_dct = {} # maps block index to actual block
        block_list = [] # records all blocks as read from the nif file in the proper order
        block_num = 0 # the current block numner

        if version < 0x0303000D:
            # skip 'Top Level Object' block type
            top_level_str = cls.SizedString()
            top_level_str.read(stream)
            top_level_str = str(top_level_str)
            if not top_level_str == "Top Level Object":
                raise cls.NifError("expected 'Top Level Object' but got '%s' instead"%top_level_str)

        while True:
            # get block name
            if version >= 0x05000001:
                if version <= 0x0A01006A:
                    dummy, = struct.unpack('<I', stream.read(4))
                    if dummy != 0:
                        raise cls.NifError('non-zero block tag 0x%08X at 0x%08X)'%(dummy, stream.tell()))
                block_type = hdr.blockTypes[hdr.blockTypeIndex[block_num]]
            else:
                block_type = cls.SizedString()
                block_type.read(stream)
                block_type = str(block_type)
            # get the block index
            if version >= 0x0303000D:
                # for these versions the block index is simply the block number
                block_index = block_num
            else:
                # earlier versions
                # the number of blocks is not in the header
                # and a special block type string marks the end of the file
                if block_type == "End Of File": break
                # read the block index, which is probably the memory
                # location of the object when it was written to
                # memory
                else:
                    block_index, = struct.unpack('<I', stream.read(4))
                    if block_dct.has_key(block_index):
                        raise cls.NifError('duplicate block index (0x%08X at 0x%08X)'%(block_index, stream.tell()))
            # create and read block
            try:
                block = getattr(cls, block_type)()
            except AttributeError:
                raise cls.NifError("unknown block type '" + block_type + "'")
            if verbose >= 1:
                print "reading block at 0x%08X..."%stream.tell()
            try:
                block.read(
                    stream,
                    version = version, user_version = user_version,
                    link_stack = link_stack, string_list = string_list)
            except:
                if verbose >= 1:
                    print "reading failed"
                if verbose >= 2:
                    print "link stack ", link_stack
                    print "block that failed:"
                    print block
                elif verbose >= 1:
                    print block.__class__
                raise
            block_dct[block_index] = block
            block_list.append(block)
            if verbose >= 2:
                print block
            elif verbose >= 1:
                print block.__class__
            # check block size
            if version >= 0x14020007:
                if block.getSize(version = version, user_version = user_version) != hdr.blockSize[block_num]:
                    raise cls.NifError('block size check failed: corrupt nif file?')
            # check if we are done
            block_num += 1
            if version >= 0x0303000D:
                if block_num >= hdr.numBlocks: break

        # read footer
        ftr = cls.Footer()
        ftr.read(
            stream,
            version = version, user_version = user_version,
            link_stack = link_stack)

        # check if we are at the end of the file
        if stream.read(1) != '':
            raise cls.NifError('end of file not reached: corrupt nif file?')

        # fix links
        for block in block_list:
            block.fixLinks(
                version = version, user_version = user_version,
                block_dct = block_dct, link_stack = link_stack)
        ftr.fixLinks(
            version = version, user_version = user_version,
            block_dct = block_dct, link_stack= link_stack)
        if link_stack != []:
            raise cls.NifError('not all links have been popped from the stack (bug?)')
        # return root objects
        roots = []
        if version >= 0x0303000D:
            for root in ftr.roots:
                roots.append(root)
        else:
            if block_num > 0:
                roots.append(block_list[0])
        return roots

    @classmethod
    def write(cls, stream, version = None, user_version = None, roots = None, verbose = 0):
        # set up index and type dictionary
        block_list = [] # list of all blocks to be written
        block_index_dct = {} # maps block to block index
        block_type_list = [] # list of all block type strings
        block_type_dct = {} # maps block to block type string index
        string_list = []
        for root in roots:
            cls._makeBlockList(version, user_version, root, block_list, block_index_dct, block_type_list, block_type_dct)
            for block in root.tree():
                string_list.extend(
                    block.getStrings(
                        version = version, user_version = user_version))
        string_list = list(set(string_list)) # ensure unique elements

        # set up header
        hdr = cls.Header()
        hdr.userVersion = user_version # TODO dedicated type for userVersion similar to FileVersion
        # for oblivion CS; apparently this is the version of the bhk blocks
        hdr.userVersion2 = 11
        hdr.numBlocks = len(block_list)
        hdr.numBlockTypes = len(block_type_list)
        hdr.blockTypes.updateSize()
        for i, block_type in enumerate(block_type_list):
            hdr.blockTypes[i] = block_type
        hdr.blockTypeIndex.updateSize()
        for i, block in enumerate(block_list):
            hdr.blockTypeIndex[i] = block_type_dct[block]
        hdr.numStrings = len(string_list)
        if string_list:
            hdr.maxStringLength = max([len(s) for s in string_list])
        else:
            hdr.maxStringLength = 0
        hdr.strings.updateSize()
        for i, s in enumerate(string_list):
            hdr.strings[i] = s
        hdr.blockSize.updateSize()
        for i, block in enumerate(block_list):
            hdr.blockSize[i] = block.getSize(version = version, user_version = user_version)
        if verbose >= 2:
            print hdr

        # set up footer
        ftr = cls.Footer()
        ftr.numRoots = len(roots)
        ftr.roots.updateSize()
        for i, root in enumerate(roots):
            ftr.roots[i] = root

        # write the file
        hdr.write(
            stream,
            version = version, user_version = user_version,
            block_index_dct = block_index_dct)
        if version < 0x0303000D:
            s = cls.SizedString()
            s.setValue("Top Level Object")
            s.write(stream)
        for block in block_list:
            if version >= 0x05000001:
                if version <= 0x0A01006A:
                    # write zero dummy separator
                    stream.write('\x00\x00\x00\x00')
            else:
                # write block type string
                s = cls.SizedString()
                assert(block_type_list[block_type_dct[block]] == block.__class__.__name__) # debug
                s.setValue(block.__class__.__name__)
                s.write(stream)
            # write block index
            if verbose >= 1:
                print "writing block %i..."%block_index_dct[block]
            if version < 0x0303000D:
                stream.write(struct.pack('<i', block_index_dct[block])[0])
            # write block
            block.write(
                stream,
                version = version, user_version = user_version,
                block_index_dct = block_index_dct, string_list = string_list)
        if version < 0x0303000D:
            s = cls.SizedString()
            s.setValue("End Of File")
            s.write(stream)
        ftr.write(
            stream,
            version = version, user_version = user_version,
            block_index_dct = block_index_dct)

    @classmethod
    def _makeBlockList(cls, version, user_version, root, block_list, block_index_dct, block_type_list, block_type_dct):
        """This is a helper function for write to set up the list of all blocks,
        the block index map, and the block type map."""
        # block already listed? if so, return
        if root in block_list: return
        # add block type to block type dictionary
        block_type = root.__class__.__name__
        try:
            block_type_dct[root] = block_type_list.index(block_type)
        except ValueError:
            block_type_dct[root] = len(block_type_list)
            block_type_list.append(block_type)
        # add non-havok blocks before children
        if not isinstance(root, cls.bhkRefObject):
            if version >= 0x0303000D:
                block_index_dct[root] = len(block_list)
            else:
                block_index_dct[root] = id(root)
            block_list.append(root)
        # add children
        for child in root.getRefs(version = version, user_version = user_version):
            cls._makeBlockList(version, user_version, child, block_list, block_index_dct, block_type_list, block_type_dct)
        # add havok block after children (required for oblivion)
        if isinstance(root, cls.bhkRefObject):
            if version >= 0x0303000D:
                block_index_dct[root] = len(block_list)
            else:
                block_index_dct[root] = id(root)
            block_list.append(root)

    @classmethod
    def walk(cls, top, topdown = True, onerror = None, verbose = 0):
        """A generator which yields the roots of all files in directory top
        whose filename matches the regular expression re_filename. The argument
        top can also be a file instead of a directory. The argument onerror,
        if set, will be called if cls.read raises an exception (errors coming
        from os.walk will be ignored)."""
        for version, user_version, f, roots in cls.walkFile(top, topdown, onerror, verbose):
            yield roots

    @classmethod
    def walkFile(cls, top, topdown = True, onerror = None, verbose = 0, mode = 'rb'):
        """Like walk, but returns more information:
        version, user_version, f, and roots.

        Note that the caller is not responsible for closing stream.

        walkFile is for instance used by runtest.py to implement the
        testFile-style tests which must access the file after the file has been
        read."""
        # filter for recognizing nif files by extension
        # .kf are nif files containing keyframes
        # .kfa are nif files containing keyframes in DAoC style
        # .nifcache are Empire Earth II nif files
        re_nif = re.compile(r'^.*\.(nif|kf|kfa|nifcache)$', re.IGNORECASE)
        # now walk over all these files in directory top
        for filename in Utils.walk(top, topdown, onerror = None, re_filename = re_nif):
            if verbose >= 1: print "reading %s"%filename
            stream = open(filename, mode)
            try:
                # get the version
                version, user_version = cls.getVersion(stream)
                if version >= 0:
                    # we got it, so now read the nif file
                    if verbose >= 2: print "version 0x%08X"%version
                    try:
                        # return (version, user_version, stream, roots)
                        yield (version, user_version, stream,
                               cls.read(
                                   stream,
                                   version = version,
                                   user_version = user_version))
                    except StandardError, e:
                        # an error occurred during reading
                        # this should not happen: means that the file is
                        # corrupt, or that the xml is corrupt
                        # so we call onerror
                        if verbose >= 1:
                            print """
Warning: read failed due to either a corrupt nif file, a corrupt nif.xml,
or a bug in NifFormat library."""
                        if verbose >= 2:
                            Utils.hexDump(stream)
                        if onerror == None:
                            pass # ignore the error
                        else:
                            onerror(e)
                # getting version failed, do not raise an exception
                # but tell user what happened
                elif version == -1:
                    if verbose >= 1: print 'version not supported'
                else:
                    if verbose >= 1: print 'not a nif file'
            finally:
                stream.close()
