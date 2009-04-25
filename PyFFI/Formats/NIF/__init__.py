"""
:mod:`PyFFI.Formats.NIF` --- NetImmerse/Gamebryo (.nif and .kf)
===============================================================

Regression tests
----------------

These tests are used to check for functionality and bugs in the library.
They also provide code examples which you may find useful.

Read a NIF file
^^^^^^^^^^^^^^^

>>> stream = open('tests/nif/test.nif', 'rb')
>>> data = NifFormat.Data()
>>> # inspect is optional; it will not read the actual blocks
>>> data.inspect(stream)
>>> hex(data.version)
'0x14010003'
>>> data.user_version
0
>>> [blocktype for blocktype in data.header.blockTypes]
['NiNode', 'NiTriShape', 'NiTriShapeData']
>>> data.roots # blocks have not been read yet, so this is an empty list
[]
>>> data.read(stream)
>>> for root in data.roots:
...     for block in root.tree():
...         if isinstance(block, NifFormat.NiNode):
...             print(block.name)
test
>>> stream.close()

Parse all NIF files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in NifFormat.walkData('tests/nif'):
...     try:
...         # the replace call makes the doctest also pass on windows
...         print("reading %s" % stream.name.replace("\\\\", "/"))
...         data.read(stream)
...     except StandardError:
...         print("Warning: read failed due corrupt file, corrupt format description, or bug.")
reading tests/nif/invalid.nif
Warning: read failed due corrupt file, corrupt format description, or bug.
reading tests/nif/test.nif
reading tests/nif/test_centerradius.nif
reading tests/nif/test_check_tangentspace1.nif
reading tests/nif/test_check_tangentspace2.nif
reading tests/nif/test_check_tangentspace3.nif
reading tests/nif/test_check_tangentspace4.nif
reading tests/nif/test_convexverticesshape.nif
reading tests/nif/test_dump_tex.nif
reading tests/nif/test_fix_clampmaterialalpha.nif
reading tests/nif/test_fix_detachhavoktristripsdata.nif
reading tests/nif/test_fix_disableparallax.nif
reading tests/nif/test_fix_ffvt3rskinpartition.nif
reading tests/nif/test_fix_mergeskeletonroots.nif
reading tests/nif/test_fix_tangentspace.nif
reading tests/nif/test_fix_texturepath.nif
reading tests/nif/test_mopp.nif
reading tests/nif/test_opt_dupgeomdata.nif
reading tests/nif/test_opt_dupverts.nif
reading tests/nif/test_opt_emptyproperties.nif
reading tests/nif/test_opt_mergeduplicates.nif
reading tests/nif/test_skincenterradius.nif

Create a NIF model from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
>>> stream = TemporaryFile()
>>> nifdata = NifFormat.Data(version=0x14010003, user_version=10)
>>> nifdata.roots = [root]
>>> nifdata.write(stream)
>>> stream.close()

Get list of versions and games
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for vnum in sorted(NifFormat.versions.values()):
...     print('0x%08X' % vnum)
0x02030000
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
0x0A010065
0x0A01006A
0x0A020000
0x0A040001
0x14000004
0x14000005
0x14010003
0x14020007
0x14020008
0x14030001
0x14030002
0x14030003
0x14030006
0x14030009
>>> for game, versions in sorted(NifFormat.games.items(), key=lambda x: x[0]):
...     print("%s " % game + " ".join('0x%08X' % vnum for vnum in versions))
? 0x0A000103
Atlantica 0x14020008
Axis and Allies 0x0A010000
Civilization IV 0x04020002 0x04020100 0x04020200 0x0A000100 0x0A010000 \
0x0A020000 0x14000004
Culpa Innata 0x04020200
Dark Age of Camelot 0x02030000 0x03000300 0x03010000 0x0401000C 0x04020100 0x04020200 \
0x0A010000
Emerge 0x14020007 0x14020008 0x14030001 0x14030002 0x14030003 0x14030006
Empire Earth II 0x04020200
Empire Earth III 0x14020007 0x14020008
Entropia Universe 0x0A010000
Fallout 3 0x14020007
Freedom Force 0x04000000 0x04000002
Freedom Force vs. the 3rd Reich 0x0A010000
Kohan 2 0x0A010000
Loki 0x0A020000
Megami Tensei: Imagine 0x14010003
Morrowind 0x04000002
Oblivion 0x0303000D 0x0A000102 0x0A010065 0x0A01006A 0x0A020000 0x14000004 \
0x14000005
Prison Tycoon 0x0A020000
Pro Cycling Manager 0x0A020000
Red Ocean 0x0A020000
Sid Meier's Railroads 0x14000004
Star Trek: Bridge Commander 0x03000000 0x03010000
The Guild 2 0x0A010000
Warhammer 0x14030009
Wildlife Park 2 0x0A010000 0x0A020000
Worldshift 0x0A040001
Zoo Tycoon 2 0x0A000100

Reading an unsupported nif file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> stream = open('tests/nif/invalid.nif', 'rb')
>>> data = NifFormat.Data()
>>> data.inspect(stream) # the file seems ok on inspection
>>> data.read(stream) # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
NifError: ...
>>> stream.close()

Template types
^^^^^^^^^^^^^^

>>> block = NifFormat.NiTextKeyExtraData()
>>> block.numTextKeys = 1
>>> block.textKeys.updateSize()
>>> block.textKeys[0].time = 1.0
>>> block.textKeys[0].value = 'hi'

Links
^^^^^

>>> NifFormat.NiNode._hasLinks
True
>>> NifFormat.NiBone._hasLinks
True
>>> skelroot = NifFormat.NiNode()
>>> geom = NifFormat.NiTriShape()
>>> geom.skinInstance = NifFormat.NiSkinInstance()
>>> geom.skinInstance.skeletonRoot = skelroot
>>> [block.__class__.__name__ for block in geom.getRefs()]
['NiSkinInstance']
>>> [block.__class__.__name__ for block in geom.getLinks()]
['NiSkinInstance']
>>> [block.__class__.__name__ for block in geom.skinInstance.getRefs()]
[]
>>> [block.__class__.__name__ for block in geom.skinInstance.getLinks()]
['NiNode']

Strings
^^^^^^^

>>> extra = NifFormat.NiTextKeyExtraData()
>>> extra.numTextKeys = 2
>>> extra.textKeys.updateSize()
>>> extra.textKeys[0].time = 0.0
>>> extra.textKeys[0].value = "start"
>>> extra.textKeys[1].time = 2.0
>>> extra.textKeys[1].value = "end"
>>> extra.getStrings()
['start', 'end']
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, NIF File Format Library and Tools.
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

import logging
import os
import re
import struct
import sys
import warnings
import weakref

import PyFFI.ObjectModels.Common
import PyFFI.ObjectModels.FileFormat
import PyFFI.ObjectModels.XML.FileFormat
import PyFFI.Utils.TriStrip
from PyFFI.ObjectModels.Editable import EditableBoolComboBox
from PyFFI.ObjectModels.Graph import EdgeFilter
from PyFFI.ObjectModels.XML.Basic import BasicBase

class NifFormat(PyFFI.ObjectModels.XML.FileFormat.XmlFileFormat):
    """This class contains the generated classes from the xml."""

    xmlFileName = 'nif.xml'
    # where to look for nif.xml and in what order: NIFXMLPATH env var,
    # or NifFormat module directory
    xmlFilePath = [os.getenv('NIFXMLPATH'), os.path.dirname(__file__)]
    clsFilePath = os.path.dirname(__file__) # path of class customizers
    # filter for recognizing nif files by extension
    # .kf are nif files containing keyframes
    # .kfa are nif files containing keyframes in DAoC style
    # .nifcache are Empire Earth II nif files
    RE_FILENAME = re.compile(r'^.*\.(nif|kf|kfa|nifcache)$', re.IGNORECASE)
    # used for comparing floats
    _EPSILON = 0.0001

    # basic types
    int = PyFFI.ObjectModels.Common.Int
    uint = PyFFI.ObjectModels.Common.UInt
    byte = PyFFI.ObjectModels.Common.UByte # not a typo
    char = PyFFI.ObjectModels.Common.Char
    short = PyFFI.ObjectModels.Common.Short
    ushort = PyFFI.ObjectModels.Common.UShort
    float = PyFFI.ObjectModels.Common.Float
    BlockTypeIndex = PyFFI.ObjectModels.Common.UShort
    StringIndex = PyFFI.ObjectModels.Common.UInt
    SizedString = PyFFI.ObjectModels.Common.SizedString

    # implementation of nif-specific basic types

    class StringOffset(PyFFI.ObjectModels.Common.Int):
        """This is just an integer with -1 as default value."""
        def __init__(self, **kwargs):
            PyFFI.ObjectModels.Common.Int.__init__(self, **kwargs)
            self.setValue(-1)

    class bool(BasicBase, EditableBoolComboBox):
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
            BasicBase.__init__(self, **kwargs)
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
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1
            if ver > 0x04000002:
                return 1
            else:
                return 4

        def getHash(self, **kwargs):
            return self._value

        def read(self, stream, **kwargs):
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1
            if ver > 0x04000002:
                value, = struct.unpack('<B', stream.read(1))
            else:
                value, = struct.unpack('<I', stream.read(4))
            self._value = bool(value)

        def write(self, stream, **kwargs):
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1
            if ver > 0x04000002:
                stream.write(struct.pack('<B', int(self._value)))
            else:
                stream.write(struct.pack('<I', int(self._value)))

    class Flags(PyFFI.ObjectModels.Common.UShort):
        def __str__(self):
            return hex(self.getValue())

    class Ref(BasicBase):
        """Reference to another block."""
        _isTemplate = True
        _hasLinks = True
        _hasRefs = True
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)
            self._template = kwargs.get("template")
            self.setValue(None)

        def getValue(self):
            return self._value

        def setValue(self, value):
            if value is None:
                self._value = None
            else:
                if not isinstance(value, self._template):
                    raise TypeError('expected an instance of %s \
but got instance of %s' % (self._template, value.__class__))
                self._value = value

        def getSize(self, **kwargs):
            return 4

        def getHash(self, **kwargs):
            if self.getValue():
                return self.getValue().getHash(**kwargs)
            else:
                return None

        def read(self, stream, **kwargs):
            self.setValue(None) # fixLinks will set this field
            block_index, = struct.unpack('<i', stream.read(4))
            kwargs.get('link_stack', []).append(block_index)

        def write(self, stream, **kwargs):
            """Write block reference.

            :keyword block_index_dct: The dictionary of block indices
                (block -> index).
            """
            if self.getValue() is None:
                # nothing to point to
                try:
                    ver = kwargs['data'].version
                except KeyError:
                    ver = -1
                if ver >= 0x0303000D:
                    stream.write('\xff\xff\xff\xff') # link by number
                else:
                    stream.write('\x00\x00\x00\x00') # link by pointer
            else:
                stream.write(struct.pack(
                    '<i', kwargs.get('block_index_dct')[self.getValue()]))

        def fixLinks(self, **kwargs):
            """Fix block links.

            :keyword link_stack: The link stack.
            :keyword block_dct: The block dictionary (index -> block).
            """
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1

            block_index = kwargs.get('link_stack').pop(0)
            # case when there's no link
            if ver >= 0x0303000D:
                if block_index == -1: # link by block number
                    self.setValue(None)
                    return
            else:
                if block_index == 0: # link by pointer
                    self.setValue(None)
                    return
            # other case: look up the link and check the link type
            block = kwargs.get('block_dct')[block_index]
            if not isinstance(block, self._template):
                raise TypeError('expected an instance of %s but got instance of %s'%(self._template, block.__class__))
            self.setValue(block)

        def getLinks(self, **kwargs):
            val = self.getValue()
            if val is not None:
                return [val]
            else:
                return []

        def getRefs(self, **kwargs):
            val = self.getValue()
            if val is not None:
                return [val]
            else:
                return []

        def replaceGlobalNode(self, oldbranch, newbranch,
                              edge_filter=EdgeFilter()):
            """
            >>> from PyFFI.Formats.NIF import NifFormat
            >>> x = NifFormat.NiNode()
            >>> y = NifFormat.NiNode()
            >>> z = NifFormat.NiNode()
            >>> x.addChild(y)
            >>> x.children[0] is y
            True
            >>> x.children[0] is z
            False
            >>> x.replaceGlobalNode(y, z)
            >>> x.children[0] is y
            False
            >>> x.children[0] is z
            True
            >>> x.replaceGlobalNode(z, None)
            >>> x.children[0] is None
            True
            """
            if self.getValue() is oldbranch:
                # setValue takes care of template type
                self.setValue(newbranch)
                #print("replacing", repr(oldbranch), "->", repr(newbranch))
            if self.getValue() is not None:
                self.getValue().replaceGlobalNode(oldbranch, newbranch)

        def getDetailDisplay(self):
            # return the node itself, if it is not None
            if self.getValue() is not None:
                return self.getValue()
            else:
                return "None"

    class Ptr(Ref):
        """A weak reference to another block, used to point up the hierarchy tree. The reference is not returned by the L{getRefs} function to avoid infinite recursion."""
        _isTemplate = True
        _hasLinks = True
        _hasRefs = False

        # use weak reference to aid garbage collection

        def getValue(self):
            return self._value() if self._value is not None else None

        def setValue(self, value):
            if value is None:
                self._value = None
            else:
                if not isinstance(value, self._template):
                    raise TypeError('expected an instance of %s \
but got instance of %s' % (self._template, value.__class__))
                self._value = weakref.ref(value)

        def __str__(self):
            # avoid infinite recursion
            return '%s instance at 0x%08X'%(self._value.__class__, id(self._value))

        def getRefs(self, **kwargs):
            return []

        def getHash(self, **kwargs):
            return None

        def replaceGlobalNode(self, oldbranch, newbranch,
                              edge_filter=EdgeFilter()):
            # overridden to avoid infinite recursion
            if self.getValue() is oldbranch:
                self.setValue(newbranch)
                #print("replacing", repr(oldbranch), "->", repr(newbranch))

    class LineString(BasicBase):
        """Basic type for strings ending in a newline character (0x0a).

        >>> from tempfile import TemporaryFile
        >>> f = TemporaryFile()
        >>> l = NifFormat.LineString()
        >>> f.write('abcdefg\\x0a'.encode())
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
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)
            self.setValue('')

        def getValue(self):
            return self._value

        def setValue(self, value):
            self._value = PyFFI.ObjectModels.Common._asBytes(value).rstrip('\x0a'.encode("ascii"))

        def __str__(self):
            return PyFFI.ObjectModels.Common._asStr(self._value)

        def getSize(self, **kwargs):
            return len(self._value) + 1 # +1 for trailing endline

        def getHash(self, **kwargs):
            return self.getValue()

        def read(self, stream, **kwargs):
            self._value = stream.readline().rstrip('\x0a'.encode("ascii"))

        def write(self, stream, **kwargs):
            stream.write(self._value)
            stream.write("\x0a".encode("ascii"))

    class HeaderString(BasicBase):
        def __str__(self):
            return 'NetImmerse/Gamebryo File Format, Version x.x.x.x'

        def getDetailDisplay(self):
            return self.__str__()

        def getHash(self, **kwargs):
            return None

        def read(self, stream, **kwargs):
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1

            version_string = self.versionString(ver)
            s = stream.read(len(version_string) + 1)
            if s != (version_string + '\x0a').encode("ascii"):
                raise ValueError(
                    "invalid NIF header: expected '%s' but got '%s'"
                    % (version_string, s[:-1]))

        def write(self, stream, **kwargs):
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1

            stream.write(self.versionString(ver).encode("ascii"))
            stream.write('\x0a'.encode("ascii"))

        def getSize(self, **kwargs):
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1

            return len(self.versionString(ver).encode("ascii")) + 1

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
                raise RuntimeError('no string for version %s'%version)
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
            if ver != kwargs['data'].version:
                raise ValueError(
                    'invalid version number: expected 0x%08X but got 0x%08X'
                    % (kwargs['data'].version, ver))

        def write(self, stream, **kwargs):
            stream.write(struct.pack('<I', kwargs['data'].version))

        def getDetailDisplay(self):
            return 'x.x.x.x'

    class ShortString(BasicBase):
        """Another type for strings."""
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)
            self._value = ''

        def getValue(self):
            return self._value

        def setValue(self, value):
            val = PyFFI.ObjectModels.Common._asBytes(value)
            if len(val) > 254:
                raise ValueError('string too long')
            self._value = val

        def __str__(self):
            return PyFFI.ObjectModels.Common._asStr(self._value)

        def getSize(self, **kwargs):
            # length byte + string chars + zero byte
            return len(self._value) + 2

        def getHash(self, **kwargs):
            return self.getValue()

        def read(self, stream, **kwargs):
            n, = struct.unpack('<B', stream.read(1))
            self._value = stream.read(n).rstrip('\x00'.encode("ascii"))

        def write(self, stream, **kwargs):
            stream.write(struct.pack('<B', len(self._value)+1))
            stream.write(self._value + '\x00'.encode("ascii"))

    class string(SizedString):
        _hasStrings = True

        def getSize(self, **kwargs):
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1
            if ver >= 0x14010003:
                return 4
            else:
                return 4 + len(self._value)

        def read(self, stream, **kwargs):
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1

            n, = struct.unpack('<i', stream.read(4))
            if ver >= 0x14010003:
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
            try:
                ver = kwargs['data'].version
            except KeyError:
                ver = -1

            if ver >= 0x14010003:
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
        """A file path."""
        def getHash(self, **kwargs):
            """Returns a case insensitive hash value."""
            return self.getValue().lower()

    class ByteArray(BasicBase):
        """Array (list) of bytes. Implemented as basic type to speed up reading
        and also to prevent data to be dumped by __str__."""
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)
            self.setValue("".encode()) # b'' for > py25

        def getValue(self):
            return self._value

        def setValue(self, value):
            assert(isinstance(value, basestring))
            self._value = value

        def getSize(self, **kwargs):
            return len(self._value) + 4

        def getHash(self, **kwargs):
            return self._value.__hash__()

        def read(self, stream, **kwargs):
            size, = struct.unpack('<I', stream.read(4))
            self._value = stream.read(size)

        def write(self, stream, **kwargs):
            stream.write(struct.pack('<I', len(self._value)))
            stream.write(self._value)

        def __str__(self):
            return "< %i Bytes >" % len(self._value)

    class ByteMatrix(BasicBase):
        """Matrix of bytes. Implemented as basic type to speed up reading
        and to prevent data being dumped by __str__."""
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)
            self.setValue([])

        def getValue(self):
            return self._value

        def setValue(self, value):
            assert(isinstance(value, list))
            if value:
                size1 = len(value[0])
            for x in value:
                assert(isinstance(value, basestring))
                assert(len(x) == size1)
            self._value = value # should be a list of strings of bytes

        def getSize(self, **kwargs):
            if len(self._value) == 0:
                return 8
            else:
                return len(self._value) * len(self._value[0]) + 8

        def getHash(self, **kwargs):
            return tuple( x.__hash__() for x in self._value )

        def read(self, stream, **kwargs):
            size1, = struct.unpack('<I', stream.read(4))
            size2, = struct.unpack('<I', stream.read(4))
            self._value = []
            for i in xrange(size2):
                self._value.append(stream.read(size1))

        def write(self, stream, **kwargs):
            if self._value:
                stream.write(struct.pack('<I', len(self._value[0])))
            else:
                stream.write(struct.pack('<I', 0))
            stream.write(struct.pack('<I', len(self._value)))
            for x in self._value:
                stream.write(x)

        def __str__(self):
            size1 = len(self._value[0]) if self._value else 0
            size2 = len(self._value)
            return "< %ix%i Bytes >" % (size2, size1)

    @classmethod
    def vercondFilter(cls, expression):
        if expression == "Version":
            return "version"
        elif expression == "User Version":
            return "user_version"
        elif expression == "User Version 2":
            return "user_version2"
        ver = cls.versionNumber(expression)
        if ver < 0:
            # not supported?
            raise ValueError(
                "cannot recognize version expression '%s'" % expression)
        else:
            return ver

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        :param version_str: The version string.
        :type version_str: str
        :return: A version integer.

        >>> hex(NifFormat.versionNumber('3.14.15.29'))
        '0x30e0f1d'
        >>> hex(NifFormat.versionNumber('1.2'))
        '0x1020000'
        >>> hex(NifFormat.versionNumber('3.03'))
        '0x3000300'
        """

        # 3.03 case is special
        if version_str == '3.03':
            return 0x03000300

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

    # exceptions
    class NifError(StandardError):
        """Standard nif exception class."""
        pass

    class Data(PyFFI.ObjectModels.FileFormat.FileFormat.Data):
        """A class to contain the actual nif data.

        Note that L{header} and L{blocks} are not automatically kept
        in sync with the rest of the nif data, but they are
        resynchronized when calling L{write}.

        :ivar version: The nif version.
        :type version: ``int``
        :ivar user_version: The nif user version.
        :type user_version: ``int``
        :ivar user_version2: The nif user version 2.
        :type user_version2: ``int``
        :ivar roots: List of root blocks.
        :type roots: ``list`` of L{NifFormat.NiObject}
        :ivar header: The nif header.
        :type header: L{NifFormat.Header}
        :ivar blocks: List of blocks.
        :type blocks: ``list`` of L{NifFormat.NiObject}
        """

        class VersionUInt(PyFFI.ObjectModels.Common.UInt):
            def setValue(self, value):
                if value is None:
                    self._value = None
                else:
                    PyFFI.ObjectModels.Common.UInt.setValue(self, value)

            def __str__(self):
                if self._value is None:
                    return "None"
                else:
                    return "0x%08X" % self.getValue()

            def getDetailDisplay(self):
                return self.__str__()

        def __init__(self, version=0x04000002, user_version=0, user_version2=0):
            """Initialize nif data. By default, this creates an empty
            nif document of the given version and user version.

            :param version: The version.
            :type version: ``int``
            :param user_version: The user version.
            :type user_version: ``int``
            """
            # the version numbers are stored outside the header structure
            self._version_value_ = self.VersionUInt()
            self._version_value_.setValue(version)
            self._user_version_value_ = self.VersionUInt()
            self._user_version_value_.setValue(user_version)
            self._user_version_2_value_ = self.VersionUInt()
            self._user_version_2_value_.setValue(user_version2)
            # create new header
            self.header = NifFormat.Header()
            # empty list of root blocks (this encodes the footer)
            self.roots = []
            # empty list of blocks
            self.blocks = []

        def _getVersion(self):
            return self._version_value_.getValue()
        def _setVersion(self, value):
            self._version_value_.setValue(value)
            
        def _getUserVersion(self):
            return self._user_version_value_.getValue()
        def _setUserVersion(self, value):
            self._user_version_value_.setValue(value)

        def _getUserVersion2(self):
            return self._user_version_2_value_.getValue()
        def _setUserVersion2(self, value):
            self._user_version_2_value_.setValue(value)

        version = property(_getVersion, _setVersion)
        user_version = property(_getUserVersion, _setUserVersion)
        user_version2 = property(_getUserVersion2, _setUserVersion2)

        # new functions

        def inspectVersionOnly(self, stream):
            """This function checks the version only, and is faster
            than the usual inspect function (which reads the full
            header). Sets the L{version} and L{user_version} instance
            variables if the stream contains a valid nif file.

            Call this function if you simply wish to check that a file is
            a nif file without having to parse even the header.

            :param stream: The stream from which to read.
            :type stream: ``file``
            @raise C{ValueError}: If the stream does not contain a nif file.
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
                raise ValueError("not a nif file")
            try:
                ver = NifFormat.versionNumber(version_str)
            except:
                raise ValueError("nif version %s not supported" % version_str)
            if not ver in NifFormat.versions.values():
                raise ValueError("nif version %s not supported" % version_str)
            # check version integer and user version
            userver = 0
            userver2 = 0
            if ver >= 0x0303000D:
                ver_int = None
                try:
                    stream.readline(64)
                    ver_int, = struct.unpack('<I', stream.read(4))
                    if ver_int != ver:
                        raise ValueError("""\
corrupted nif file: header version string does not correspond with
header version field""")
                    if ver >= 0x14000004:
                        stream.read(1)
                    if ver >= 0x0A010000:
                        userver, = struct.unpack('<I', stream.read(4))
                        if userver in (10, 11):
                            stream.read(4) # number of blocks
                            userver2, = struct.unpack('<I', stream.read(4))
                finally:
                    stream.seek(pos)
            self.version = ver
            self.user_version = userver
            self.user_version2 = userver2

        # GlobalNode

        def getGlobalChildNodes(self, edge_filter=EdgeFilter()):
            return (root for root in self.roots)

        # DetailNode

        def replaceGlobalNode(self, oldbranch, newbranch,
                              edge_filter=EdgeFilter()):
            for i, root in enumerate(self.roots):
                if root is oldbranch:
                    self.roots[i] = newbranch
                else:
                    root.replaceGlobalNode(oldbranch, newbranch,
                                           edge_filter=edge_filter)

        def getDetailChildNodes(self, edge_filter=EdgeFilter()):
            yield self._version_value_
            yield self._user_version_value_
            yield self._user_version_2_value_
            yield self.header

        def getDetailChildNames(self, edge_filter=EdgeFilter()):
            yield "Version"
            yield "User Version"
            yield "User Version 2"
            yield "Header"

        # overriding PyFFI.ObjectModels.FileFormat.FileFormat.Data methods

        def inspect(self, stream):
            """Quickly checks whether the stream appears to contain
            nif data, and read the nif header. Resets stream to original position.

            Call this function if you only need to inspect the header of the nif.

            :param stream: The file to inspect.
            :type stream: ``file``
            """
            pos = stream.tell()
            try:
                self.inspectVersionOnly(stream)
                self.header.read(stream, data=self)
            finally:
                stream.seek(pos)

        def read(self, stream, verbose=0):
            """Read a nif file. Does not reset stream position.

            :param stream: The stream from which to read.
            :type stream: ``file``
            :param verbose: The level of verbosity.
            :type verbose: ``int``
            """
            logger = logging.getLogger("pyffi.nif.data")
            # read header
            logger.debug("Reading header at 0x%08X" % stream.tell())
            self.inspectVersionOnly(stream)
            self.header.read(stream, data=self)
            #logger.debug("%s" % self.header)

            # list of root blocks
            # for versions < 3.3.0.13 this list is updated through the
            # "Top Level Object" string while reading the blocks
            # for more recent versions, this list is updated at the end when the
            # footer is read
            self.roots = []

            # read the blocks
            link_stack = [] # list of indices, as they are added to the stack
            string_list = [str(s) for s in self.header.strings]
            block_dct = {} # maps block index to actual block
            self.blocks = [] # records all blocks as read from file in order
            block_num = 0 # the current block numner

            while True:
                if self.version < 0x0303000D:
                    # check if this is a 'Top Level Object'
                    pos = stream.tell()
                    top_level_str = NifFormat.SizedString()
                    top_level_str.read(stream)
                    top_level_str = str(top_level_str)
                    if top_level_str == "Top Level Object":
                        is_root = True
                    else:
                        is_root = False
                        stream.seek(pos)
                else:
                    # signal as no root for now, roots are added when the footer
                    # is read
                    is_root = False

                # get block name
                if self.version >= 0x05000001:
                    if self.version <= 0x0A01006A:
                        dummy, = struct.unpack('<I', stream.read(4))
                        if dummy != 0:
                            raise NifFormat.NifError(
                                'non-zero block tag 0x%08X at 0x%08X)'
                                %(dummy, stream.tell()))
                    # note the 0xfff mask: required for the NiPhysX blocks
                    block_type = self.header.blockTypes[
                        self.header.blockTypeIndex[block_num] & 0xfff]
                else:
                    block_type = NifFormat.SizedString()
                    block_type.read(stream)
                    block_type = str(block_type.getValue())
                # get the block index
                if self.version >= 0x0303000D:
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
                            raise NifFormat.NifError(
                                'duplicate block index (0x%08X at 0x%08X)'
                                %(block_index, stream.tell()))
                # create and read block
                try:
                    block = getattr(NifFormat, block_type)()
                except AttributeError:
                    raise NifFormat.NifError(
                        "unknown block type '%s'" % block_type)
                logger.debug("Reading %s block at 0x%08X"
                             % (block_type, stream.tell()))
                try:
                    block.read(
                        stream,
                        data=self,
                        link_stack=link_stack, string_list=string_list)
                except:
                    logger.exception("Reading %s failed" % block.__class__)
                    #logger.error("link stack: %s" % link_stack)
                    #logger.error("block that failed:")
                    #logger.error("%s" % block)
                    raise
                block_dct[block_index] = block
                self.blocks.append(block)
                # check block size
                if self.version >= 0x14020007:
                    logger.debug("Checking block size")
                    calculated_size = block.getSize(data=self)
                    if calculated_size != self.header.blockSize[block_num]:
                        extra_size = self.header.blockSize[block_num] - calculated_size
                        logger.error("""\
Block size check failed: corrupt nif file or bad nif.xml?""")
                        logger.error("""\
Skipping %i bytes in %s""" % (extra_size, block.__class__.__name__))
                        # skip bytes that were missed
                        stream.seek(extra_size, 1)
                # add block to roots if flagged as such
                if is_root:
                    self.roots.append(block)
                # check if we are done
                block_num += 1
                if self.version >= 0x0303000D:
                    if block_num >= self.header.numBlocks:
                        break

            # read footer
            ftr = NifFormat.Footer()
            ftr.read(
                stream,
                data=self,
                link_stack = link_stack)

            # check if we are at the end of the file
            if stream.read(1) != '':
                raise NifFormat.NifError('end of file not reached: corrupt nif file?')

            # fix links in blocks and footer (header has no links)
            for block in self.blocks:
                block.fixLinks(
                    data=self,
                    block_dct = block_dct, link_stack = link_stack)
            ftr.fixLinks(
                data=self,
                block_dct = block_dct, link_stack= link_stack)
            # the link stack should be empty now
            if link_stack:
                raise NifFormat.NifError('not all links have been popped from the stack (bug?)')
            # add root objects in footer to roots list
            if self.version >= 0x0303000D:
                for root in ftr.roots:
                    self.roots.append(root)

        def write(self, stream, verbose=0):
            """Write a nif file. The L{header} and the L{blocks} are recalculated
            from the tree at L{roots} (e.g. list of block types, number of blocks,
            list of block types, list of strings, list of block sizes etc.).

            :param stream: The stream to which to write.
            :type stream: file
            :param verbose: The level of verbosity.
            :type verbose: int
            """
            logger = logging.getLogger("pyffi.nif.data")
            # set up index and type dictionary
            self.blocks = [] # list of all blocks to be written
            block_index_dct = {} # maps block to block index
            block_type_list = [] # list of all block type strings
            block_type_dct = {} # maps block to block type string index
            string_list = []
            for root in self.roots:
                self._makeBlockList(root,
                                    block_index_dct,
                                    block_type_list, block_type_dct)
                for block in root.tree():
                    string_list.extend(
                        block.getStrings(
                            data=self))
            string_list = list(set(string_list)) # ensure unique elements
            #print(string_list) # debug

            self.header.userVersion = self.user_version # TODO dedicated type for userVersion similar to FileVersion
            # for oblivion CS; apparently this is the version of the bhk blocks
            self.header.userVersion2 = self.user_version2
            self.header.numBlocks = len(self.blocks)
            self.header.numBlockTypes = len(block_type_list)
            self.header.blockTypes.updateSize()
            for i, block_type in enumerate(block_type_list):
                self.header.blockTypes[i] = block_type
            self.header.blockTypeIndex.updateSize()
            for i, block in enumerate(self.blocks):
                self.header.blockTypeIndex[i] = block_type_dct[block]
            self.header.numStrings = len(string_list)
            if string_list:
                self.header.maxStringLength = max([len(s) for s in string_list])
            else:
                self.header.maxStringLength = 0
            self.header.strings.updateSize()
            for i, s in enumerate(string_list):
                self.header.strings[i] = s
            self.header.blockSize.updateSize()
            for i, block in enumerate(self.blocks):
                self.header.blockSize[i] = block.getSize(data=self)
            #if verbose >= 2:
            #    print(hdr)

            # set up footer
            ftr = NifFormat.Footer()
            ftr.numRoots = len(self.roots)
            ftr.roots.updateSize()
            for i, root in enumerate(self.roots):
                ftr.roots[i] = root

            # write the file
            logger.debug("Writing header")
            #logger.debug("%s" % self.header)
            self.header.write(
                stream,
                data=self,
                block_index_dct = block_index_dct)
            for block in self.blocks:
                # signal top level object if block is a root object
                if self.version < 0x0303000D and block in self.roots:
                    s = NifFormat.SizedString()
                    s.setValue("Top Level Object")
                    s.write(stream)
                if self.version >= 0x05000001:
                    if self.version <= 0x0A01006A:
                        # write zero dummy separator
                        stream.write('\x00\x00\x00\x00')
                else:
                    # write block type string
                    s = NifFormat.SizedString()
                    assert(block_type_list[block_type_dct[block]] \
                           == block.__class__.__name__) # debug
                    s.setValue(block.__class__.__name__)
                    s.write(stream)
                # write block index
                logger.debug("Writing %s block" % block.__class__.__name__)
                if self.version < 0x0303000D:
                    stream.write(struct.pack('<i', block_index_dct[block]))
                # write block
                block.write(
                    stream,
                    data=self,
                    block_index_dct = block_index_dct, string_list = string_list)
            if self.version < 0x0303000D:
                s = NifFormat.SizedString()
                s.setValue("End Of File")
                s.write(stream)
            ftr.write(
                stream,
                data=self,
                block_index_dct = block_index_dct)

        def _makeBlockList(
            self, root, block_index_dct, block_type_list, block_type_dct):
            """This is a helper function for write to set up the list of all blocks,
            the block index map, and the block type map.

            :param root: The root block, whose tree is to be added to
                the block list.
            :type root: L{NifFormat.NiObject}
            :param block_index_dct: Dictionary mapping blocks in self.blocks to
                their block index.
            :type block_index_dct: dict
            :param block_type_list: List of all block types.
            :type block_type_list: list of str
            :param block_type_dct: Dictionary mapping blocks in self.blocks to
                their block type index.
            :type block_type_dct: dict
            """

            def _blockChildBeforeParent(block):
                """Determine whether block comes before its parent or not, depending
                on the block type.

                @todo: Move to the L{NifFormat.Data} class.

                :param block: The block to test.
                :type block: L{NifFormat.NiObject}
                :return: ``True`` if child should come first, ``False`` otherwise.
                """
                return (isinstance(block, NifFormat.bhkRefObject)
                        and not isinstance(block, NifFormat.bhkConstraint))

            # block already listed? if so, return
            if root in self.blocks:
                return
            # add block type to block type dictionary
            block_type = root.__class__.__name__
            try:
                block_type_dct[root] = block_type_list.index(block_type)
            except ValueError:
                block_type_dct[root] = len(block_type_list)
                block_type_list.append(block_type)

            # special case: add bhkConstraint entities before bhkConstraint
            # (these are actually links, not refs)
            if isinstance(root, NifFormat.bhkConstraint):
                for entity in root.entities:
                    self._makeBlockList(
                        entity, block_index_dct, block_type_list, block_type_dct)

            # add children that come before the block
            for child in root.getRefs(data=self):
                if _blockChildBeforeParent(child):
                    self._makeBlockList(
                        child, block_index_dct, block_type_list, block_type_dct)

            # add the block
            if self.version >= 0x0303000D:
                block_index_dct[root] = len(self.blocks)
            else:
                block_index_dct[root] = id(root)
            self.blocks.append(root)

            # add children that come after the block
            for child in root.getRefs(data=self):
                if not _blockChildBeforeParent(child):
                    self._makeBlockList(
                        child, block_index_dct, block_type_list, block_type_dct)

    # extensions of generated structures

    # XXX this is a *very* ugly hack so we can change the base classes of
    # XXX anything that derives from object
    # XXX see http://bugs.python.org/issue672115
    class object(object):
        pass

    class Header(object):
        def hasBlockType(self, block_type):
            """Check if header has a particular block type.

            @raise ValueError: If number of block types is zero (only nif versions
                10.0.1.0 and up store block types in header).

            :param block_type: The block type.
            :type block_type: L{NifFormat.NiObject}
            :return: ``True`` if the header's list of block types has the given
                block type, or a subclass of it. ``False`` otherwise.
            :rtype: ``bool``
            """
            # check if we can check the block types at all
            if self.numBlockTypes == 0:
                raise ValueError("header does not store any block types")
            # quick first check, without hierarchy, using simple string comparisons
            if block_type.__name__ in self.blockTypes:
                return True
            # slower check, using isinstance
            for data_block_type in self.blockTypes:
                if issubclass(getattr(NifFormat, data_block_type), block_type):
                    return True
            # requested block type is not in nif
            return False

    class Matrix33(object):
        def asList(self):
            """Return matrix as 3x3 list."""
            return [
                [self.m11, self.m12, self.m13],
                [self.m21, self.m22, self.m23],
                [self.m31, self.m32, self.m33]
                ]

        def asTuple(self):
            """Return matrix as 3x3 tuple."""
            return (
                (self.m11, self.m12, self.m13),
                (self.m21, self.m22, self.m23),
                (self.m31, self.m32, self.m33)
                )

        def __str__(self):
            return (
                "[ %6.3f %6.3f %6.3f ]\n"
                "[ %6.3f %6.3f %6.3f ]\n"
                "[ %6.3f %6.3f %6.3f ]\n"
                % (self.m11, self.m12, self.m13,
                   self.m21, self.m22, self.m23,
                   self.m31, self.m32, self.m33))

        def setIdentity(self):
            """Set to identity matrix."""
            self.m11 = 1.0
            self.m12 = 0.0
            self.m13 = 0.0
            self.m21 = 0.0
            self.m22 = 1.0
            self.m23 = 0.0
            self.m31 = 0.0
            self.m32 = 0.0
            self.m33 = 1.0

        def isIdentity(self):
            """Return ``True`` if the matrix is close to identity."""
            if  (abs(self.m11 - 1.0) > NifFormat._EPSILON
                 or abs(self.m12) > NifFormat._EPSILON
                 or abs(self.m13) > NifFormat._EPSILON
                 or abs(self.m21) > NifFormat._EPSILON
                 or abs(self.m22 - 1.0) > NifFormat._EPSILON
                 or abs(self.m23) > NifFormat._EPSILON
                 or abs(self.m31) > NifFormat._EPSILON
                 or abs(self.m32) > NifFormat._EPSILON
                 or abs(self.m33 - 1.0) > NifFormat._EPSILON):
                return False
            else:
                return True

        def getCopy(self):
            """Return a copy of the matrix."""
            mat = NifFormat.Matrix33()
            mat.m11 = self.m11
            mat.m12 = self.m12
            mat.m13 = self.m13
            mat.m21 = self.m21
            mat.m22 = self.m22
            mat.m23 = self.m23
            mat.m31 = self.m31
            mat.m32 = self.m32
            mat.m33 = self.m33
            return mat

        def getTranspose(self):
            """Get transposed of the matrix."""
            mat = NifFormat.Matrix33()
            mat.m11 = self.m11
            mat.m12 = self.m21
            mat.m13 = self.m31
            mat.m21 = self.m12
            mat.m22 = self.m22
            mat.m23 = self.m32
            mat.m31 = self.m13
            mat.m32 = self.m23
            mat.m33 = self.m33
            return mat

        def isScaleRotation(self):
            """Returns true if the matrix decomposes nicely into scale * rotation."""
            # NOTE: 0.01 instead of NifFormat._EPSILON to work around bad nif files

            # calculate self * self^T
            # this should correspond to
            # (scale * rotation) * (scale * rotation)^T
            # = scale^2 * rotation * rotation^T
            # = scale^2 * 3x3 identity matrix
            self_transpose = self.getTranspose()
            mat = self * self_transpose

            # off diagonal elements should be zero
            if (abs(mat.m12) + abs(mat.m13)
                + abs(mat.m21) + abs(mat.m23)
                + abs(mat.m31) + abs(mat.m32)) > 0.01:
                return False

            # diagonal elements should be equal (to scale^2)
            if abs(mat.m11 - mat.m22) + abs(mat.m22 - mat.m33) > 0.01:
                return False

            return True

        def isRotation(self):
            """Returns ``True`` if the matrix is a rotation matrix
            (a member of SO(3))."""
            # NOTE: 0.01 instead of NifFormat._EPSILON to work around bad nif files

            if not self.isScaleRotation():
                return False
            if abs(self.getDeterminant() - 1.0) > 0.01:
                return False
            return True

        def getDeterminant(self):
            """Return determinant."""
            return (self.m11*self.m22*self.m33
                    +self.m12*self.m23*self.m31
                    +self.m13*self.m21*self.m32
                    -self.m31*self.m22*self.m13
                    -self.m21*self.m12*self.m33
                    -self.m11*self.m32*self.m23)

        def getScale(self):
            """Gets the scale (assuming isScaleRotation is true!)."""
            scale = self.getDeterminant()
            if scale < 0:
                return -((-scale)**(1.0/3.0))
            else:
                return scale**(1.0/3.0)

        def getScaleRotation(self):
            """Decompose the matrix into scale and rotation, where scale is a float
            and rotation is a C{Matrix33}. Returns a pair (scale, rotation)."""
            rot = self.getCopy()
            scale = self.getScale()
            if abs(scale) < NifFormat._EPSILON:
                raise ZeroDivisionError('scale is zero, unable to obtain rotation')
            rot /= scale
            return (scale, rot)

        def setScaleRotation(self, scale, rotation):
            """Compose the matrix as the product of scale * rotation."""
            if not isinstance(scale, (float, int, long)):
                raise TypeError('scale must be float')
            if not isinstance(rotation, NifFormat.Matrix33):
                raise TypeError('rotation must be Matrix33')

            if not rotation.isRotation():
                raise ValueError('rotation must be rotation matrix')

            self.m11 = rotation.m11 * scale
            self.m12 = rotation.m12 * scale
            self.m13 = rotation.m13 * scale
            self.m21 = rotation.m21 * scale
            self.m22 = rotation.m22 * scale
            self.m23 = rotation.m23 * scale
            self.m31 = rotation.m31 * scale
            self.m32 = rotation.m32 * scale
            self.m33 = rotation.m33 * scale

        def getScaleQuat(self):
            """Decompose matrix into scale and quaternion."""
            scale, rot = self.getScaleRotation()
            quat = NifFormat.Quaternion()
            trace = 1.0 + rot.m11 + rot.m22 + rot.m33

            if trace > NifFormat._EPSILON:
                s = (trace ** 0.5) * 2
                quat.x = -( rot.m32 - rot.m23 ) / s
                quat.y = -( rot.m13 - rot.m31 ) / s
                quat.z = -( rot.m21 - rot.m12 ) / s
                quat.w = 0.25 * s
            elif rot.m11 > max((rot.m22, rot.m33)):
                s  = (( 1.0 + rot.m11 - rot.m22 - rot.m33 ) ** 0.5) * 2
                quat.x = 0.25 * s
                quat.y = (rot.m21 + rot.m12 ) / s
                quat.z = (rot.m13 + rot.m31 ) / s
                quat.w = -(rot.m32 - rot.m23 ) / s
            elif rot.m22 > rot.m33:
                s  = (( 1.0 + rot.m22 - rot.m11 - rot.m33 ) ** 0.5) * 2
                quat.x = (rot.m21 + rot.m12 ) / s
                quat.y = 0.25 * s
                quat.z = (rot.m32 + rot.m23 ) / s
                quat.w = -(rot.m13 - rot.m31 ) / s
            else:
                s  = (( 1.0 + rot.m33 - rot.m11 - rot.m22 ) ** 0.5) * 2
                quat.x = (rot.m13 + rot.m31 ) / s
                quat.y = (rot.m32 + rot.m23 ) / s
                quat.z = 0.25 * s
                quat.w = -(rot.m21 - rot.m12 ) / s

            return scale, quat


        def getInverse(self):
            """Get inverse (assuming isScaleRotation is true!)."""
            # transpose inverts rotation but keeps the scale
            # dividing by scale^2 inverts the scale as well
            return self.getTranspose() / (self.m11**2 + self.m12**2 + self.m13**2)

        def __mul__(self, rhs):
            if isinstance(rhs, (float, int, long)):
                mat = NifFormat.Matrix33()
                mat.m11 = self.m11 * rhs
                mat.m12 = self.m12 * rhs
                mat.m13 = self.m13 * rhs
                mat.m21 = self.m21 * rhs
                mat.m22 = self.m22 * rhs
                mat.m23 = self.m23 * rhs
                mat.m31 = self.m31 * rhs
                mat.m32 = self.m32 * rhs
                mat.m33 = self.m33 * rhs
                return mat
            elif isinstance(rhs, NifFormat.Vector3):
                raise TypeError("matrix*vector not supported;\
    please use left multiplication (vector*matrix)")
            elif isinstance(rhs, NifFormat.Matrix33):
                mat = NifFormat.Matrix33()
                mat.m11 = self.m11 * rhs.m11 + self.m12 * rhs.m21 + self.m13 * rhs.m31
                mat.m12 = self.m11 * rhs.m12 + self.m12 * rhs.m22 + self.m13 * rhs.m32
                mat.m13 = self.m11 * rhs.m13 + self.m12 * rhs.m23 + self.m13 * rhs.m33
                mat.m21 = self.m21 * rhs.m11 + self.m22 * rhs.m21 + self.m23 * rhs.m31
                mat.m22 = self.m21 * rhs.m12 + self.m22 * rhs.m22 + self.m23 * rhs.m32
                mat.m23 = self.m21 * rhs.m13 + self.m22 * rhs.m23 + self.m23 * rhs.m33
                mat.m31 = self.m31 * rhs.m11 + self.m32 * rhs.m21 + self.m33 * rhs.m31
                mat.m32 = self.m31 * rhs.m12 + self.m32 * rhs.m22 + self.m33 * rhs.m32
                mat.m33 = self.m31 * rhs.m13 + self.m32 * rhs.m23 + self.m33 * rhs.m33
                return mat
            else:
                raise TypeError(
                    "do not know how to multiply Matrix33 with %s"%rhs.__class__)

        def __div__(self, rhs):
            if isinstance(rhs, (float, int, long)):
                mat = NifFormat.Matrix33()
                mat.m11 = self.m11 / rhs
                mat.m12 = self.m12 / rhs
                mat.m13 = self.m13 / rhs
                mat.m21 = self.m21 / rhs
                mat.m22 = self.m22 / rhs
                mat.m23 = self.m23 / rhs
                mat.m31 = self.m31 / rhs
                mat.m32 = self.m32 / rhs
                mat.m33 = self.m33 / rhs
                return mat
            else:
                raise TypeError(
                    "do not know how to divide Matrix33 by %s"%rhs.__class__)

        def __rmul__(self, lhs):
            if isinstance(lhs, (float, int, long)):
                return self * lhs # commutes
            else:
                raise TypeError(
                    "do not know how to multiply %s with Matrix33"%lhs.__class__)

        def __eq__(self, mat):
            if not isinstance(mat, NifFormat.Matrix33):
                raise TypeError(
                    "do not know how to compare Matrix33 and %s"%mat.__class__)
            if (abs(self.m11 - mat.m11) > NifFormat._EPSILON
                or abs(self.m12 - mat.m12) > NifFormat._EPSILON
                or abs(self.m13 - mat.m13) > NifFormat._EPSILON
                or abs(self.m21 - mat.m21) > NifFormat._EPSILON
                or abs(self.m22 - mat.m22) > NifFormat._EPSILON
                or abs(self.m23 - mat.m23) > NifFormat._EPSILON
                or abs(self.m31 - mat.m31) > NifFormat._EPSILON
                or abs(self.m32 - mat.m32) > NifFormat._EPSILON
                or abs(self.m33 - mat.m33) > NifFormat._EPSILON):
                return False
            return True

        def __ne__(self, mat):
            return not self.__eq__(mat)

        def __sub__(self, x):
            if isinstance(x, (NifFormat.Matrix33)):
                m = NifFormat.Matrix33()
                m.m11 = self.m11 - x.m11
                m.m12 = self.m12 - x.m12
                m.m13 = self.m13 - x.m13
                m.m21 = self.m21 - x.m21
                m.m22 = self.m22 - x.m22
                m.m23 = self.m23 - x.m23
                m.m31 = self.m31 - x.m31
                m.m32 = self.m32 - x.m32
                m.m33 = self.m33 - x.m33
                return m
            elif isinstance(x, (int, long, float)):
                m = NifFormat.Matrix33()
                m.m11 = self.m11 - x
                m.m12 = self.m12 - x
                m.m13 = self.m13 - x
                m.m21 = self.m21 - x
                m.m22 = self.m22 - x
                m.m23 = self.m23 - x
                m.m31 = self.m31 - x
                m.m32 = self.m32 - x
                m.m33 = self.m33 - x
                return m
            else:
                raise TypeError("do not know how to substract Matrix33 and %s"
                                % x.__class__)

        def supNorm(self):
            """Calculate supremum norm of matrix (maximum absolute value of all
            entries)."""
            return max(max(abs(elem) for elem in row)
                       for row in self.asList())

    class Vector3(object):
        def asList(self):
            return [self.x, self.y, self.z]

        def asTuple(self):
            return (self.x, self.y, self.z)

        def norm(self):
            return (self.x*self.x + self.y*self.y + self.z*self.z) ** 0.5

        def normalize(self):
            norm = self.norm()
            if norm < NifFormat._EPSILON:
                raise ZeroDivisionError('cannot normalize vector %s'%self)
            self.x /= norm
            self.y /= norm
            self.z /= norm

        def getCopy(self):
            v = NifFormat.Vector3()
            v.x = self.x
            v.y = self.y
            v.z = self.z
            return v

        def __str__(self):
            return "[ %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z)

        def __mul__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.Vector3()
                v.x = self.x * x
                v.y = self.y * x
                v.z = self.z * x
                return v
            elif isinstance(x, NifFormat.Vector3):
                return self.x * x.x + self.y * x.y + self.z * x.z
            elif isinstance(x, NifFormat.Matrix33):
                v = NifFormat.Vector3()
                v.x = self.x * x.m11 + self.y * x.m21 + self.z * x.m31
                v.y = self.x * x.m12 + self.y * x.m22 + self.z * x.m32
                v.z = self.x * x.m13 + self.y * x.m23 + self.z * x.m33
                return v
            elif isinstance(x, NifFormat.Matrix44):
                return self * x.getMatrix33() + x.getTranslation()
            else:
                raise TypeError("do not know how to multiply Vector3 with %s"%x.__class__)

        def __rmul__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.Vector3()
                v.x = x * self.x
                v.y = x * self.y
                v.z = x * self.z
                return v
            else:
                raise TypeError("do not know how to multiply %s and Vector3"%x.__class__)

        def __div__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.Vector3()
                v.x = self.x / x
                v.y = self.y / x
                v.z = self.z / x
                return v
            else:
                raise TypeError("do not know how to divide Vector3 and %s"%x.__class__)

        def __add__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.Vector3()
                v.x = self.x + x
                v.y = self.y + x
                v.z = self.z + x
                return v
            elif isinstance(x, NifFormat.Vector3):
                v = NifFormat.Vector3()
                v.x = self.x + x.x
                v.y = self.y + x.y
                v.z = self.z + x.z
                return v
            else:
                raise TypeError("do not know how to add Vector3 and %s"%x.__class__)

        def __radd__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.Vector3()
                v.x = x + self.x
                v.y = x + self.y
                v.z = x + self.z
                return v
            else:
                raise TypeError("do not know how to add %s and Vector3"%x.__class__)

        def __sub__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.Vector3()
                v.x = self.x - x
                v.y = self.y - x
                v.z = self.z - x
                return v
            elif isinstance(x, NifFormat.Vector3):
                v = NifFormat.Vector3()
                v.x = self.x - x.x
                v.y = self.y - x.y
                v.z = self.z - x.z
                return v
            else:
                raise TypeError("do not know how to substract Vector3 and %s"%x.__class__)

        def __rsub__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.Vector3()
                v.x = x - self.x
                v.y = x - self.y
                v.z = x - self.z
                return v
            else:
                raise TypeError("do not know how to substract %s and Vector3"%x.__class__)

        def __neg__(self):
            v = NifFormat.Vector3()
            v.x = -self.x
            v.y = -self.y
            v.z = -self.z
            return v

        # cross product
        def crossproduct(self, x):
            if isinstance(x, NifFormat.Vector3):
                v = NifFormat.Vector3()
                v.x = self.y*x.z - self.z*x.y
                v.y = self.z*x.x - self.x*x.z
                v.z = self.x*x.y - self.y*x.x
                return v
            else:
                raise TypeError("do not know how to calculate crossproduct of Vector3 and %s"%x.__class__)

        def __eq__(self, x):
            if isinstance(x, type(None)):
                return False
            if not isinstance(x, NifFormat.Vector3):
                raise TypeError("do not know how to compare Vector3 and %s"%x.__class__)
            if abs(self.x - x.x) > NifFormat._EPSILON: return False
            if abs(self.y - x.y) > NifFormat._EPSILON: return False
            if abs(self.z - x.z) > NifFormat._EPSILON: return False
            return True

        def __ne__(self, x):
            return not self.__eq__(x)

    class Vector4(object):
        """
        Regression tests
        ----------------

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> vec = NifFormat.Vector4()
        >>> vec.x = 1.0
        >>> vec.y = 2.0
        >>> vec.z = 3.0
        >>> vec.w = 4.0
        >>> print(vec)
        [  1.000  2.000  3.000  4.000 ]
        >>> vec.asList()
        [1.0, 2.0, 3.0, 4.0]
        >>> vec.asTuple()
        (1.0, 2.0, 3.0, 4.0)
        >>> print(vec.getVector3())
        [  1.000  2.000  3.000 ]
        >>> vec2 = NifFormat.Vector4()
        >>> vec == vec2
        False
        >>> vec2.x = 1.0
        >>> vec2.y = 2.0
        >>> vec2.z = 3.0
        >>> vec2.w = 4.0
        >>> vec == vec2
        True
        """

        def asList(self):
            return [self.x, self.y, self.z, self.w]

        def asTuple(self):
            return (self.x, self.y, self.z, self.w)

        def getCopy(self):
            v = NifFormat.Vector4()
            v.x = self.x
            v.y = self.y
            v.z = self.z
            v.w = self.w
            return v

        def getVector3(self):
            v = NifFormat.Vector3()
            v.x = self.x
            v.y = self.y
            v.z = self.z
            return v

        def __str__(self):
            return "[ %6.3f %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z, self.w)

        def __eq__(self, rhs):
            if isinstance(rhs, type(None)):
                return False
            if not isinstance(rhs, NifFormat.Vector4):
                raise TypeError(
                    "do not know how to compare Vector4 and %s" % rhs.__class__)
            if abs(self.x - rhs.x) > NifFormat._EPSILON: return False
            if abs(self.y - rhs.y) > NifFormat._EPSILON: return False
            if abs(self.z - rhs.z) > NifFormat._EPSILON: return False
            if abs(self.w - rhs.w) > NifFormat._EPSILON: return False
            return True

        def __ne__(self, rhs):
            return not self.__eq__(rhs)

    class SkinPartition(object):
        def getTriangles(self):
            """Get list of triangles of this partition.
            """
            # strips?
            if self.numStrips:
                for tri in PyFFI.Utils.TriStrip.triangulate(self.strips):
                    yield tri
            # no strips, do triangles
            else:
                for tri in self.triangles:
                    yield (tri.v1, tri.v2, tri.v3)

        def getMappedTriangles(self):
            """Get list of triangles of this partition (mapping into the
            geometry data vertex list).
            """
            for tri in self.getTriangles():
                yield tuple(self.vertexMap[v_index] for v_index in tri)
