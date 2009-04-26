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

from itertools import izip, repeat
import logging
import math # math.pi
import os
import re
import struct
import sys
import warnings
import weakref

import PyFFI.Formats.DDS
import PyFFI.ObjectModels.Common
import PyFFI.ObjectModels.FileFormat
import PyFFI.ObjectModels.XML.FileFormat
import PyFFI.Utils.Inertia
from PyFFI.Utils.MathUtils import * # XXX todo get rid of from XXX import *
import PyFFI.Utils.Mopp
import PyFFI.Utils.TriStrip
import PyFFI.Utils.QuickHull
# XXX convert the following to absolute imports
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
                    raise TypeError(
                        'expected an instance of %s but got instance of %s'
                        % (self._template, value.__class__))
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
                    raise TypeError(
                        'expected an instance of %s but got instance of %s'
                        % (self._template, value.__class__))
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
                        raise ValueError(
                            "corrupted nif file: header version string "
                            "does not correspond with header version field")
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
                        logger.error(
                            "Block size check failed: corrupt nif file "
                            "or bad nif.xml?")
                        logger.error("Skipping %i bytes in %s"
                                     % (extra_size, block.__class__.__name__))
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
                    assert(block_type_list[block_type_dct[block]]
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

    class Header:
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

    class Matrix33:
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
                raise TypeError(
                    "matrix*vector not supported; "
                    "please use left multiplication (vector*matrix)")
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

    class Vector3:
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

    class Vector4:
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

    class SkinPartition:
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

    class bhkBoxShape:
        def applyScale(self, scale):
            """Apply scale factor C{scale} on data."""
            # apply scale on dimensions
            self.dimensions.x *= scale
            self.dimensions.y *= scale
            self.dimensions.z *= scale
            self.minimumSize  *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

        def getMassCenterInertia(self, density = 1, solid = True):
            """Return mass, center, and inertia tensor."""
            # the dimensions describe half the size of the box in each dimension
            # so the length of a single edge is dimension.dir * 2
            mass, inertia = PyFFI.Utils.Inertia.getMassInertiaBox(
                (self.dimensions.x * 2, self.dimensions.y * 2, self.dimensions.z * 2),
                density = density, solid = solid)
            return mass, (0,0,0), inertia

    class bhkCapsuleShape:
        def applyScale(self, scale):
            """Apply scale factor <scale> on data."""
            # apply scale on dimensions
            self.radius *= scale
            self.radius1 *= scale
            self.radius2 *= scale
            self.firstPoint.x *= scale
            self.firstPoint.y *= scale
            self.firstPoint.z *= scale
            self.secondPoint.x *= scale
            self.secondPoint.y *= scale
            self.secondPoint.z *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

        def getMassCenterInertia(self, density = 1, solid = True):
            """Return mass, center, and inertia tensor."""
            # (assumes self.radius == self.radius1 == self.radius2)
            length = (self.firstPoint - self.secondPoint).norm()
            mass, inertia = PyFFI.Utils.Inertia.getMassInertiaCapsule(
                radius = self.radius, length = length,
                density = density, solid = solid)
            # now fix inertia so it is expressed in the right coordinates
            # need a transform that maps (0,0,length/2) on (second - first) / 2
            # and (0,0,-length/2) on (first - second)/2
            vec1 = ((self.secondPoint - self.firstPoint) / length).asTuple()
            # find an orthogonal vector to vec1
            index = min(enumerate(vec1), key=lambda val: abs(val[1]))[0]
            vec2 = vecCrossProduct(vec1, tuple((1 if i == index else 0)
                                               for i in xrange(3)))
            vec2 = vecscalarMul(vec2, 1/vecNorm(vec2))
            # find an orthogonal vector to vec1 and vec2
            vec3 = vecCrossProduct(vec1, vec2)
            # get transform matrix
            transform_transposed = (vec2, vec3, vec1) # this is effectively the transposed of our transform
            transform = matTransposed(transform_transposed)
            # check the result (debug)
            assert(vecDistance(matvecMul(transform, (0,0,1)), vec1) < 0.0001)
            assert(abs(matDeterminant(transform) - 1) < 0.0001)
            # transform the inertia tensor
            inertia = matMul(matMul(transform_transposed, inertia), transform)
            return (mass,
                    ((self.firstPoint + self.secondPoint) * 0.5).asTuple(),
                    inertia)

    class bhkConstraint:
        def getTransformAB(self, parent):
            """Returns the transform of the first entity relative to the second
            entity. Root is simply a nif block that is a common parent to both
            blocks."""
            # check entities
            if self.numEntities != 2:
                raise ValueError(
                    "cannot get tranform for constraint "
                    "that hasn't exactly 2 entities")
            # find transform of entity A relative to entity B

            # find chains from parent to A and B entities
            chainA = parent.findChain(self.entities[0])
            chainB = parent.findChain(self.entities[1])
            # validate the chains
            assert(isinstance(chainA[-1], NifFormat.bhkRigidBody))
            assert(isinstance(chainA[-2], NifFormat.NiCollisionObject))
            assert(isinstance(chainA[-3], NifFormat.NiNode))
            assert(isinstance(chainB[-1], NifFormat.bhkRigidBody))
            assert(isinstance(chainB[-2], NifFormat.NiCollisionObject))
            assert(isinstance(chainB[-3], NifFormat.NiNode))
            # return the relative transform
            return (chainA[-3].getTransform(relative_to = parent)
                    * chainB[-3].getTransform(relative_to = parent).getInverse())

    class bhkConvexVerticesShape:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < NifFormat._EPSILON: return
            for v in self.vertices:
                v.x *= scale
                v.y *= scale
                v.z *= scale
            for n in self.normals:
                n.w *= scale

        def getMassCenterInertia(self, density = 1, solid = True):
            """Return mass, center, and inertia tensor."""
            # first find an enumeration of all triangles making up the convex shape
            vertices, triangles = PyFFI.Utils.QuickHull.qhull3d(
                [vert.asTuple() for vert in self.vertices])
            # now calculate mass, center, and inertia
            return PyFFI.Utils.Inertia.getMassCenterInertiaPolyhedron(
                vertices, triangles, density = density, solid = solid)

    class bhklimitedHingeConstraint:
        def applyScale(self, scale):
            """Scale data."""
            # apply scale on transform
            self.limitedHinge.pivotA.x *= scale
            self.limitedHinge.pivotA.y *= scale
            self.limitedHinge.pivotA.z *= scale
            self.limitedHinge.pivotB.x *= scale
            self.limitedHinge.pivotB.y *= scale
            self.limitedHinge.pivotB.z *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

        def updateAB(self, parent):
            """Update the B data from the A data. The parent argument is simply a
            common parent to the entities."""
            self.limitedHinge.updateAB(self.getTransformAB(parent))

    class bhkListShape:
        def getMassCenterInertia(self, density = 1, solid = True):
            """Return center of gravity and area."""
            subshapes_mci = [ subshape.getMassCenterInertia(density = density,
                                                            solid = solid)
                              for subshape in self.subShapes ]
            total_mass = 0
            total_center = (0, 0, 0)
            total_inertia = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
            for mass, center, inertia in subshapes_mci:
                total_mass += mass
                total_center = vecAdd(total_center,
                                      vecscalarMul(center, mass / total_mass))
                total_inertia = matAdd(total_inertia, inertia)
            return total_mass, total_center, total_inertia

        def addShape(self, shape, front = False):
            """Add shape to list."""
            # check if it's already there
            if shape in self.subShapes: return
            # increase number of shapes
            num_shapes = self.numSubShapes
            self.numSubShapes = num_shapes + 1
            self.subShapes.updateSize()
            # add the shape
            if not front:
                self.subShapes[num_shapes] = shape
            else:
                for i in xrange(num_shapes, 0, -1):
                    self.subShapes[i] = self.subShapes[i-1]
                self.subShapes[0] = shape
            # expand list of unknown ints as well
            self.numUnknownInts = num_shapes + 1
            self.unknownInts.updateSize()

        def removeShape(self, shape):
            """Remove a shape from the shape list."""
            # get list of shapes excluding the shape to remove
            shapes = [s for s in self.subShapes if s != shape]
            # set subShapes to this list
            self.numSubShapes = len(shapes)
            self.subShapes.updateSize()
            for i, s in enumerate(shapes):
                self.subShapes[i] = s
            # update unknown ints
            self.numUnknownInts = len(shapes)
            self.unknownInts.updateSize()

    class bhkMalleableConstraint:
        def applyScale(self, scale):
            """Scale data."""
            # apply scale on transform
            self.ragdoll.pivotA.x *= scale
            self.ragdoll.pivotA.y *= scale
            self.ragdoll.pivotA.z *= scale
            self.ragdoll.pivotB.x *= scale
            self.ragdoll.pivotB.y *= scale
            self.ragdoll.pivotB.z *= scale
            self.limitedHinge.pivotA.x *= scale
            self.limitedHinge.pivotA.y *= scale
            self.limitedHinge.pivotA.z *= scale
            self.limitedHinge.pivotB.x *= scale
            self.limitedHinge.pivotB.y *= scale
            self.limitedHinge.pivotB.z *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

        def updateAB(self, parent):
            """Update the B data from the A data."""
            transformAB = self.getTransformAB(parent)
            self.limitedHinge.updateAB(transform)
            self.ragdoll.updateAB(transform)

    class bhkMoppBvTreeShape:
        def getMassCenterInertia(self, density = 1, solid = True):
            """Return mass, center of gravity, and inertia tensor."""
            return self.shape.getMassCenterInertia(density = density, solid = solid)

        def updateOriginScale(self):
            """Update scale and origin."""
            minx = min(v.x for v in self.shape.data.vertices)
            miny = min(v.y for v in self.shape.data.vertices)
            minz = min(v.z for v in self.shape.data.vertices)
            maxx = max(v.x for v in self.shape.data.vertices)
            maxy = max(v.y for v in self.shape.data.vertices)
            maxz = max(v.z for v in self.shape.data.vertices)
            self.origin.x = minx - 0.1
            self.origin.y = miny - 0.1
            self.origin.z = minz - 0.1
            self.scale = (256*256*254) / (0.2+max([maxx-minx,maxy-miny,maxz-minz]))

        def updateMopp(self):
            """Update the MOPP data, scale, and origin, and welding info.

            @deprecated: use updateMoppWelding instead
            """
            self.updateMoppWelding()

        def updateMoppWelding(self):
            """Update the MOPP data, scale, and origin, and welding info."""
            logger = logging.getLogger("pyffi.mopp")

            # first try with PyFFI.Utils.Mopp
            try:
                print(PyFFI.Utils.Mopp.getMopperCredits())
                # find material indices per triangle
                material_per_vertex = []
                subshapes = self.shape.subShapes
                if not subshapes:
                    # fallout 3
                    subshapes = self.shape.data.subShapes
                for subshape in subshapes:
                    material_per_vertex += [subshape.material] * subshape.numVertices
                material_per_triangle = [
                    material_per_vertex[hktri.triangle.v1]
                    for hktri in self.shape.data.triangles]
                # compute havok info
                origin, scale, mopp, welding_infos \
                = PyFFI.Utils.Mopp.getMopperOriginScaleCodeWelding(
                    [vert.asTuple() for vert in self.shape.data.vertices],
                    [(hktri.triangle.v1, hktri.triangle.v2, hktri.triangle.v3)
                     for hktri in self.shape.data.triangles],
                    material_per_triangle)
            except (OSError, RuntimeError):
                logger.exception(
                    "Havok mopp generator failed, falling back on simple mopp")
                self.updateOriginScale()
                mopp = self._makeSimpleMopp()
                # no welding info
                welding_infos = []
            else:
                # must use calculated scale and origin
                self.scale = scale
                self.origin.x = origin[0]
                self.origin.y = origin[1]
                self.origin.z = origin[2]

            # delete mopp and replace with new data
            self.moppDataSize = len(mopp)
            self.moppData.updateSize()
            for i, b in enumerate(mopp):
                self.moppData[i] = b

            # update welding information
            for hktri, welding_info in izip(self.shape.data.triangles, welding_infos):
                hktri.weldingInfo = welding_info
                

        def _makeSimpleMopp(self):
            """Make a simple mopp."""
            mopp = [] # the mopp 'assembly' script
            self._q = 256*256 / self.scale # quantization factor

            # opcodes
            BOUNDX = 0x26
            BOUNDY = 0x27
            BOUNDZ = 0x28
            TESTX = 0x10
            TESTY = 0x11
            TESTZ = 0x12

            # add first crude bounding box checks
            self._vertsceil  = [ self._moppCeil(v) for v in self.shape.data.vertices ]
            self._vertsfloor = [ self._moppFloor(v) for v in self.shape.data.vertices ]
            minx = min([ v[0] for v in self._vertsfloor ])
            miny = min([ v[1] for v in self._vertsfloor ])
            minz = min([ v[2] for v in self._vertsfloor ])
            maxx = max([ v[0] for v in self._vertsceil ])
            maxy = max([ v[1] for v in self._vertsceil ])
            maxz = max([ v[2] for v in self._vertsceil ])
            if minx < 0 or miny < 0 or minz < 0: raise ValueError("cannot update mopp tree with invalid origin")
            if maxx > 255 or maxy > 255 or maxz > 255: raise ValueError("cannot update mopp tree with invalid scale")
            mopp.extend([BOUNDZ, minz, maxz])
            mopp.extend([BOUNDY, miny, maxy])
            mopp.extend([BOUNDX, minx, maxx])

            # add tree using subsequent X-Y-Z splits
            # (slow and no noticable difference from other simple tree so deactivated)
            #tris = range(len(self.shape.data.triangles))
            #tree = self.splitTriangles(tris, [[minx,maxx],[miny,maxy],[minz,maxz]])
            #mopp += self.moppFromTree(tree)

            # add a trivial tree
            # this prevents the player of walking through the model
            # but arrows may still fly through
            numtriangles = len(self.shape.data.triangles)
            i = 0x30
            for t in xrange(numtriangles-1):
                 mopp.extend([TESTZ, maxz, 0, 1, i])
                 i += 1
                 if i == 0x50:
                     mopp.extend([0x09, 0x20]) # increment triangle offset
                     i = 0x30
            mopp.extend([i])

            return mopp

        def _moppCeil(self, v):
            moppx = int((v.x + 0.1 - self.origin.x) / self._q + 0.99999999)
            moppy = int((v.y + 0.1 - self.origin.y) / self._q + 0.99999999)
            moppz = int((v.z + 0.1 - self.origin.z) / self._q + 0.99999999)
            return [moppx, moppy, moppz]

        def _moppFloor(self, v):
            moppx = int((v.x - 0.1 - self.origin.x) / self._q)
            moppy = int((v.y - 0.1 - self.origin.y) / self._q)
            moppz = int((v.z - 0.1 - self.origin.z) / self._q)
            return [moppx, moppy, moppz]

        def splitTriangles(self, ts, bbox, dir=0):
            """Direction 0=X, 1=Y, 2=Z"""
            btest = [] # for bounding box tests
            test = [] # for branch command
            # check bounding box
            tris = [ t.triangle for t in self.shape.data.triangles ]
            tsverts = [ tris[t].v1 for t in ts] + [ tris[t].v2 for t in ts] + [ tris[t].v3 for t in ts]
            minx = min([self._vertsfloor[v][0] for v in tsverts])
            miny = min([self._vertsfloor[v][1] for v in tsverts])
            minz = min([self._vertsfloor[v][2] for v in tsverts])
            maxx = max([self._vertsceil[v][0] for v in tsverts])
            maxy = max([self._vertsceil[v][1] for v in tsverts])
            maxz = max([self._vertsceil[v][2] for v in tsverts])
            # add bounding box checks if it's reduced in a direction
            if (maxx - minx < bbox[0][1] - bbox[0][0]):
                btest += [ 0x26, minx, maxx ]
                bbox[0][0] = minx
                bbox[0][1] = maxx
            if (maxy - miny < bbox[1][1] - bbox[1][0]):
                btest += [ 0x27, miny, maxy ]
                bbox[1][0] = miny
                bbox[1][1] = maxy
            if (maxz - minz < bbox[2][1] - bbox[2][0]):
                btest += [ 0x28, minz, maxz ]
                bbox[2][0] = minz
                bbox[2][1] = maxz
            # if only one triangle, no further split needed
            if len(ts) == 1:
                if ts[0] < 32:
                    return [ btest, [ 0x30 + ts[0] ], [], [] ]
                elif ts[0] < 256:
                    return [ btest, [ 0x50, ts[0] ], [], [] ]
                else:
                    return [ btest, [ 0x51, ts[0] >> 8, ts[0] & 255 ], [], [] ]
            # sort triangles in required direction
            ts.sort(key = lambda t: max(self._vertsceil[tris[t].v1][dir], self._vertsceil[tris[t].v2][dir], self._vertsceil[tris[t].v3][dir]))
            # split into two
            ts1 = ts[:len(ts)/2]
            ts2 = ts[len(ts)/2:]
            # get maximum coordinate of small group
            ts1verts = [ tris[t].v1 for t in ts1] + [ tris[t].v2 for t in ts1] + [ tris[t].v3 for t in ts1]
            ts2verts = [ tris[t].v1 for t in ts2] + [ tris[t].v2 for t in ts2] + [ tris[t].v3 for t in ts2]
            ts1max = max([self._vertsceil[v][dir] for v in ts1verts])
            # get minimum coordinate of large group
            ts2min = min([self._vertsfloor[v][dir] for v in ts2verts])
            # set up test
            test += [0x10+dir, ts1max, ts2min]
            # set up new bounding boxes for each subtree
            # make copy
            bbox1 = [[bbox[0][0],bbox[0][1]],[bbox[1][0],bbox[1][1]],[bbox[2][0],bbox[2][1]]]
            bbox2 = [[bbox[0][0],bbox[0][1]],[bbox[1][0],bbox[1][1]],[bbox[2][0],bbox[2][1]]]
            # update bound in test direction
            bbox1[dir][1] = ts1max
            bbox2[dir][0] = ts2min
            # return result
            nextdir = dir+1
            if nextdir == 3: nextdir = 0
            return [btest, test, self.splitTriangles(ts1, bbox1, nextdir), self.splitTriangles(ts2, bbox2, nextdir)]

        def moppFromTree(self, tree):
            if tree[1][0] in xrange(0x30, 0x52):
                return tree[0] + tree[1]
            mopp = tree[0] + tree[1]
            submopp1 = self.moppFromTree(tree[2])
            submopp2 = self.moppFromTree(tree[3])
            if len(submopp1) < 256:
                mopp += [ len(submopp1) ]
                mopp += submopp1
                mopp += submopp2
            else:
                jump = len(submopp2)
                if jump <= 255:
                    mopp += [2, 0x05, jump]
                else:
                    mopp += [3, 0x06, jump >> 8, jump & 255]
                mopp += submopp2
                mopp += submopp1
            return mopp

        # ported and extended from NifVis/bhkMoppBvTreeShape.py
        def parseMopp(self, start = 0, depth = 0, toffset = 0, verbose = False):
            """The mopp data is printed to the debug channel
            while parsed. Returns list of indices into mopp data of the bytes
            processed and a list of triangle indices encountered.

            The verbose argument is ignored (and is deprecated).
            """
            class Message:
                def __init__(self):
                    self.logger = logging.getLogger("pyffi.mopp")
                    self.msg = ""

                def append(self, *args):
                    self.msg += " ".join(str(arg) for arg in args) + " "
                    return self

                def debug(self):
                    if self.msg:
                        self.logger.debug(self.msg)
                        self.msg = ""

                def error(self):
                    self.logger.error(self.msg)
                    self.msg = ""

            mopp = self.moppData # shortcut notation
            ids = [] # indices of bytes processed
            tris = [] # triangle indices
            i = start # current index
            ret = False # set to True if an opcode signals a triangle index
            while i < self.moppDataSize and not ret:
                # get opcode and print it
                code = mopp[i]
                msg = Message()
                msg.append("%4i:"%i + "  "*depth + '0x%02X ' % code)

                if code == 0x09:
                    # increment triangle offset
                    toffset += mopp[i+1]
                    msg.append(mopp[i+1])
                    msg.append('%i [ triangle offset += %i, offset is now %i ]'
                                    % (mopp[i+1], mopp[i+1], toffset))
                    ids.extend([i,i+1])
                    i += 2

                elif code in [ 0x0A ]:
                    # increment triangle offset
                    toffset += mopp[i+1]*256 + mopp[i+2]
                    msg.append(mopp[i+1],mopp[i+2])
                    msg.append('[ triangle offset += %i, offset is now %i ]'
                                    % (mopp[i+1]*256 + mopp[i+2], toffset))
                    ids.extend([i,i+1,i+2])
                    i += 3

                elif code in [ 0x0B ]:
                    # unsure about first two arguments, but the 3rd and 4th set triangle offset
                    toffset = 256*mopp[i+3] + mopp[i+4]
                    msg.append(mopp[i+1],mopp[i+2],mopp[i+3],mopp[i+4])
                    msg.append('[ triangle offset = %i ]' % toffset)
                    ids.extend([i,i+1,i+2,i+3,i+4])
                    i += 5

                elif code in xrange(0x30,0x50):
                    # triangle compact
                    msg.append('[ triangle %i ]'%(code-0x30+toffset))
                    ids.append(i)
                    tris.append(code-0x30+toffset)
                    i += 1
                    ret = True

                elif code == 0x50:
                    # triangle byte
                    msg.append(mopp[i+1])
                    msg.append('[ triangle %i ]'%(mopp[i+1]+toffset))
                    ids.extend([i,i+1])
                    tris.append(mopp[i+1]+toffset)
                    i += 2
                    ret = True

                elif code in [ 0x51 ]:
                    # triangle short
                    t = mopp[i+1]*256 + mopp[i+2] + toffset
                    msg.append(mopp[i+1],mopp[i+2])
                    msg.append('[ triangle %i ]' % t)
                    ids.extend([i,i+1,i+2])
                    tris.append(t)
                    i += 3
                    ret = True

                elif code in [ 0x53 ]:
                    # triangle short?
                    t = mopp[i+3]*256 + mopp[i+4] + toffset
                    msg.append(mopp[i+1],mopp[i+2],mopp[i+3],mopp[i+4])
                    msg.append('[ triangle %i ]' % t)
                    ids.extend([i,i+1,i+2,i+3,i+4])
                    tris.append(t)
                    i += 5
                    ret = True

                elif code in [ 0x05 ]:
                    # byte jump
                    msg.append('[ jump -> %i: ]'%(i+2+mopp[i+1]))
                    ids.extend([i,i+1])
                    i += 2+mopp[i+1]

                elif code in [ 0x06 ]:
                    # short jump
                    jump = mopp[i+1]*256 + mopp[i+2]
                    msg.append('[ jump -> %i: ]'%(i+3+jump))
                    ids.extend([i,i+1,i+2])
                    i += 3+jump

                elif code in [0x10,0x11,0x12, 0x13,0x14,0x15, 0x16,0x17,0x18, 0x19, 0x1A, 0x1B, 0x1C]:
                    # compact if-then-else with two arguments
                    msg.append(mopp[i+1], mopp[i+2])
                    if code == 0x10:
                        msg.append('[ branch X')
                    elif code == 0x11:
                        msg.append('[ branch Y')
                    elif code == 0x12:
                        msg.append('[ branch Z')
                    else:
                        msg.append('[ branch ?')
                    msg.append('-> %i: %i: ]'%(i+4,i+4+mopp[i+3]))
                    msg.debug()
                    msg.append("     " + "  "*depth + 'if:')
                    msg.debug()
                    idssub1, trissub1 = self.parseMopp(start = i+4, depth = depth+1, toffset = toffset, verbose = verbose)
                    msg.append("     " + "  "*depth + 'else:')
                    msg.debug()
                    idssub2, trissub2 = self.parseMopp(start = i+4+mopp[i+3], depth = depth+1, toffset = toffset, verbose = verbose)
                    ids.extend([i,i+1,i+2,i+3])
                    ids.extend(idssub1)
                    ids.extend(idssub2)
                    tris.extend(trissub1)
                    tris.extend(trissub2)
                    ret = True

                elif code in [0x20,0x21,0x22]:
                    # compact if-then-else with one argument
                    msg.append(mopp[i+1], '[ branch ? -> %i: %i: ]'%(i+3,i+3+mopp[i+2])).debug()
                    msg.append("     " + "  "*depth + 'if:').debug()
                    idssub1, trissub1 = self.parseMopp(start = i+3, depth = depth+1, toffset = toffset, verbose = verbose)
                    msg.append("     " + "  "*depth + 'else:').debug()
                    idssub2, trissub2 = self.parseMopp(start = i+3+mopp[i+2], depth = depth+1, toffset = toffset, verbose = verbose)
                    ids.extend([i,i+1,i+2])
                    ids.extend(idssub1)
                    ids.extend(idssub2)
                    tris.extend(trissub1)
                    tris.extend(trissub2)
                    ret = True

                elif code in [0x23,0x24,0x25]: # short if x <= a then 1; if x > b then 2;
                    jump1 = mopp[i+3] * 256 + mopp[i+4]
                    jump2 = mopp[i+5] * 256 + mopp[i+6]
                    msg.append(mopp[i+1], mopp[i+2], '[ branch ? -> %i: %i: ]'%(i+7+jump1,i+7+jump2)).debug()
                    msg.append("     " + "  "*depth + 'if:').debug()
                    idssub1, trissub1 = self.parseMopp(start = i+7+jump1, depth = depth+1, toffset = toffset, verbose = verbose)
                    msg.append("     " + "  "*depth + 'else:').debug()
                    idssub2, trissub2 = self.parseMopp(start = i+7+jump2, depth = depth+1, toffset = toffset, verbose = verbose)
                    ids.extend([i,i+1,i+2,i+3,i+4,i+5,i+6])
                    ids.extend(idssub1)
                    ids.extend(idssub2)
                    tris.extend(trissub1)
                    tris.extend(trissub2)
                    ret = True
                elif code in [0x26,0x27,0x28]:
                    msg.append(mopp[i+1], mopp[i+2])
                    if code == 0x26:
                        msg.append('[ bound X ]')
                    elif code == 0x27:
                        msg.append('[ bound Y ]')
                    elif code == 0x28:
                        msg.append('[ bound Z ]')
                    ids.extend([i,i+1,i+2])
                    i += 3
                elif code in [0x01, 0x02, 0x03, 0x04]:
                    msg.append(mopp[i+1], mopp[i+2], mopp[i+3], '[ bound XYZ? ]')
                    ids.extend([i,i+1,i+2,i+3])
                    i += 4
                else:
                    msg.append("unknown mopp code 0x%02X"%code).error()
                    msg.append("following bytes are").debug()
                    extrabytes = [mopp[j] for j in xrange(i+1,min(self.moppDataSize,i+10))]
                    extraindex = [j       for j in xrange(i+1,min(self.moppDataSize,i+10))]
                    msg.append(extrabytes).debug()
                    for b, j in zip(extrabytes, extraindex):
                        if j+b+1 < self.moppDataSize:
                            msg.append("opcode after jump %i is 0x%02X"%(b,mopp[j+b+1]), [mopp[k] for k in xrange(j+b+2,min(self.moppDataSize,j+b+11))]).debug()
                    raise ValueError("unknown mopp opcode 0x%02X"%code)

                msg.debug()

            return ids, tris

    class bhkMultiSphereShape:
        def getMassCenterInertia(self, density = 1, solid = True):
            """Return center of gravity and area."""
            subshapes_mci = [
                (mass, center, inertia)
                for (mass, inertia), center in
                izip( ( PyFFI.Utils.Inertia.getMassInertiaSphere(radius = sphere.radius,
                                                                 density = density, solid = solid)
                        for sphere in self.spheres ),
                      ( sphere.center.asTuple() for sphere in self.spheres ) ) ]
            total_mass = 0
            total_center = (0, 0, 0)
            total_inertia = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
            for mass, center, inertia in subshapes_mci:
                total_mass += mass
                total_center = vecAdd(total_center,
                                      vecscalarMul(center, mass / total_mass))
                total_inertia = matAdd(total_inertia, inertia)
            return total_mass, total_center, total_inertia

    class bhkNiTriStripsShape:
        def getMassCenterInertia(self, density = 1, solid = True):
            """Return mass, center, and inertia tensor."""
            # first find mass, center, and inertia of all shapes
            subshapes_mci = []
            for data in self.stripsData:
                subshapes_mci.append(
                    PyFFI.Utils.Inertia.getMassCenterInertiaPolyhedron(
                        [ vert.asTuple() for vert in data.vertices ],
                        [ triangle for triangle in data.getTriangles() ],
                        density = density, solid = solid))

            # now calculate mass, center, and inertia
            total_mass = 0
            total_center = (0, 0, 0)
            total_inertia = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
            for mass, center, inertia in subshapes_mci:
                total_mass += mass
                total_center = vecAdd(total_center,
                                      vecscalarMul(center, mass / total_mass))
                total_inertia = matAdd(total_inertia, inertia)
            return total_mass, total_center, total_inertia

    class bhkPackedNiTriStripsShape:
        def getMassCenterInertia(self, density = 1, solid = True):
            """Return mass, center, and inertia tensor."""
            return PyFFI.Utils.Inertia.getMassCenterInertiaPolyhedron(
                [ vert.asTuple() for vert in self.data.vertices ],
                [ ( hktriangle.triangle.v1,
                    hktriangle.triangle.v2,
                    hktriangle.triangle.v3 )
                  for hktriangle in self.data.triangles ],
                density = density, solid = solid)

        def addShape(self, triangles, normals, vertices, layer = 0, material = 0):
            """Pack the given geometry."""
            # add the shape data
            if not self.data:
                self.data = NifFormat.hkPackedNiTriStripsData()
            data = self.data
            # increase number of shapes
            num_shapes = self.numSubShapes
            self.numSubShapes = num_shapes + 1
            self.subShapes.updateSize()
            data.numSubShapes = num_shapes + 1
            data.subShapes.updateSize()
            # add the shape
            self.subShapes[num_shapes].layer = layer
            self.subShapes[num_shapes].numVertices = len(vertices)
            self.subShapes[num_shapes].material = material
            data.subShapes[num_shapes].layer = layer
            data.subShapes[num_shapes].numVertices = len(vertices)
            data.subShapes[num_shapes].material = material
            firsttriangle = data.numTriangles
            firstvertex = data.numVertices
            data.numTriangles += len(triangles)
            data.triangles.updateSize()
            for tdata, t, n in zip(data.triangles[firsttriangle:], triangles, normals):
                tdata.triangle.v1 = t[0] + firstvertex
                tdata.triangle.v2 = t[1] + firstvertex
                tdata.triangle.v3 = t[2] + firstvertex
                tdata.normal.x = n[0]
                tdata.normal.y = n[1]
                tdata.normal.z = n[2]
            data.numVertices += len(vertices)
            data.vertices.updateSize()
            for vdata, v in zip(data.vertices[firstvertex:], vertices):
                vdata.x = v[0] / 7.0
                vdata.y = v[1] / 7.0
                vdata.z = v[2] / 7.0

    class bhkRagdollConstraint:
        def applyScale(self, scale):
            """Scale data."""
            # apply scale on transform
            self.ragdoll.pivotA.x *= scale
            self.ragdoll.pivotA.y *= scale
            self.ragdoll.pivotA.z *= scale
            self.ragdoll.pivotB.x *= scale
            self.ragdoll.pivotB.y *= scale
            self.ragdoll.pivotB.z *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

        def updateAB(self, parent):
            """Update the B data from the A data."""
            self.ragdoll.updateAB(self.getTransformAB(parent))

    class bhkRigidBody:
        def applyScale(self, scale):
            """Apply scale factor <scale> on data."""
            # apply scale on transform
            self.translation.x *= scale
            self.translation.y *= scale
            self.translation.z *= scale

            # apply scale on center of gravity
            self.center.x *= scale
            self.center.y *= scale
            self.center.z *= scale

            # apply scale on inertia tensor
            self.inertia.m11 *= (scale ** 2)
            self.inertia.m12 *= (scale ** 2)
            self.inertia.m13 *= (scale ** 2)
            self.inertia.m14 *= (scale ** 2)
            self.inertia.m21 *= (scale ** 2)
            self.inertia.m22 *= (scale ** 2)
            self.inertia.m23 *= (scale ** 2)
            self.inertia.m24 *= (scale ** 2)
            self.inertia.m31 *= (scale ** 2)
            self.inertia.m32 *= (scale ** 2)
            self.inertia.m33 *= (scale ** 2)
            self.inertia.m34 *= (scale ** 2)

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

        def updateMassCenterInertia(self, density = 1, solid = True, mass = None):
            """Look at all the objects under this rigid body and update the mass,
            center of gravity, and inertia tensor accordingly. If the C{mass} parameter
            is given then the C{density} argument is ignored."""
            if not mass is None:
                density = 1

            calc_mass, center, inertia = self.shape.getMassCenterInertia(
                density = density, solid = solid)

            self.mass = calc_mass
            self.center.x, self.center.y, self.center.z = center
            self.inertia.m11 = inertia[0][0]
            self.inertia.m12 = inertia[0][1]
            self.inertia.m13 = inertia[0][2]
            self.inertia.m14 = 0
            self.inertia.m21 = inertia[1][0]
            self.inertia.m22 = inertia[1][1]
            self.inertia.m23 = inertia[1][2]
            self.inertia.m24 = 0
            self.inertia.m31 = inertia[2][0]
            self.inertia.m32 = inertia[2][1]
            self.inertia.m33 = inertia[2][2]
            self.inertia.m34 = 0

            if not mass is None:
                mass_correction = mass / calc_mass if calc_mass != 0 else 1
                self.mass = mass
                self.inertia.m11 *= mass_correction
                self.inertia.m12 *= mass_correction
                self.inertia.m13 *= mass_correction
                self.inertia.m14 *= mass_correction
                self.inertia.m21 *= mass_correction
                self.inertia.m22 *= mass_correction
                self.inertia.m23 *= mass_correction
                self.inertia.m24 *= mass_correction
                self.inertia.m31 *= mass_correction
                self.inertia.m32 *= mass_correction
                self.inertia.m33 *= mass_correction
                self.inertia.m34 *= mass_correction

    class bhkSphereShape:
        def applyScale(self, scale):
            """Apply scale factor <scale> on data."""
            # apply scale on dimensions
            self.radius *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

        def getMassCenterInertia(self, density = 1, solid = True):
            """Return mass, center, and inertia tensor."""
            # the dimensions describe half the size of the box in each dimension
            # so the length of a single edge is dimension.dir * 2
            mass, inertia = PyFFI.Utils.Inertia.getMassInertiaSphere(
                self.radius, density = density, solid = solid)
            return mass, (0,0,0), inertia

    class bhkTransformShape:
        def applyScale(self, scale):
            """Apply scale factor <scale> on data."""
            # apply scale on translation
            self.transform.m14 *= scale
            self.transform.m24 *= scale
            self.transform.m34 *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

        def getMassCenterInertia(self, density = 1, solid = True):
            """Return mass, center, and inertia tensor."""
            # get shape mass, center, and inertia
            mass, center, inertia = self.shape.getMassCenterInertia(density = density,
                                                                    solid = solid)
            # get transform matrix and translation vector
            transform = self.transform.getMatrix33().asTuple()
            transform_transposed = matTransposed(transform)
            translation = ( self.transform.m14, self.transform.m24, self.transform.m34 )
            # transform center and inertia
            center = matvecMul(transform, center)
            center = vecAdd(center, translation)
            inertia = matMul(matMul(transform_transposed, inertia), transform)
            # return updated mass center and inertia
            return mass, center, inertia

    class BSBound:
        def applyScale(self, scale):
            """Scale data."""
            self.center.x *= scale
            self.center.y *= scale
            self.center.z *= scale
            self.dimensions.x *= scale
            self.dimensions.y *= scale
            self.dimensions.z *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

    class ControllerLink:
        """
        Regression test
        ---------------

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> link = NifFormat.ControllerLink()
        >>> link.nodeNameOffset
        -1
        >>> link.setNodeName("Bip01")
        >>> link.nodeNameOffset
        0
        >>> link.getNodeName()
        'Bip01'
        >>> link.nodeName
        'Bip01'
        >>> link.setNodeName("Bip01 Tail")
        >>> link.nodeNameOffset
        6
        >>> link.getNodeName()
        'Bip01 Tail'
        >>> link.nodeName
        'Bip01 Tail'
        """
        def _getString(self, offset):
            """A wrapper around stringPalette.palette.getString. Used by getNodeName
            etc. Returns the string at given offset."""
            if offset == -1:
                return ''

            if not self.stringPalette:
                return ''

            return self.stringPalette.palette.getString(offset)

        def _addString(self, text):
            """Wrapper for stringPalette.palette.addString. Used by setNodeName etc.
            Returns offset of string added."""
            # create string palette if none exists yet
            if not self.stringPalette:
                self.stringPalette = NifFormat.NiStringPalette()
            # add the string and return the offset
            return self.stringPalette.palette.addString(text)

        def getNodeName(self):
            """Return the node name.

            >>> # a doctest
            >>> from PyFFI.Formats.NIF import NifFormat
            >>> link = NifFormat.ControllerLink()
            >>> link.stringPalette = NifFormat.NiStringPalette()
            >>> palette = link.stringPalette.palette
            >>> link.nodeNameOffset = palette.addString("Bip01")
            >>> link.getNodeName()
            'Bip01'

            >>> # another doctest
            >>> from PyFFI.Formats.NIF import NifFormat
            >>> link = NifFormat.ControllerLink()
            >>> link.nodeName = "Bip01"
            >>> link.getNodeName()
            'Bip01'
            """
            if self.nodeName:
                return self.nodeName
            else:
                return self._getString(self.nodeNameOffset)

        def setNodeName(self, text):
            self.nodeName = text
            self.nodeNameOffset = self._addString(text)

        def getPropertyType(self):
            if self.propertyType:
                return self.propertyType
            else:
                return self._getString(self.propertyTypeOffset)

        def setPropertyType(self, text):
            self.propertyType = text
            self.propertyTypeOffset = self._addString(text)

        def getControllerType(self):
            if self.controllerType:
                return self.controllerType
            else:
                return self._getString(self.controllerTypeOffset)

        def setControllerType(self, text):
            self.controllerType = text
            self.controllerTypeOffset = self._addString(text)

        def getVariable1(self):
            if self.variable1:
                return self.variable1
            else:
                return self._getString(self.variable1Offset)

        def setVariable1(self, text):
            self.variable1 = text
            self.variable1Offset = self._addString(text)

        def getVariable2(self):
            if self.variable2:
                return self.variable2
            else:
                return self._getString(self.variable2Offset)

        def setVariable2(self, text):
            self.variable2 = text
            self.variable2Offset = self._addString(text)

    class hkPackedNiTriStripsData:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < NifFormat._EPSILON:
                return
            for vert in self.vertices:
                vert.x *= scale
                vert.y *= scale
                vert.z *= scale

    class InertiaMatrix:
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
            return(
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
            self.m14 = 0.0
            self.m21 = 0.0
            self.m22 = 1.0
            self.m23 = 0.0
            self.m24 = 0.0
            self.m31 = 0.0
            self.m32 = 0.0
            self.m33 = 1.0
            self.m34 = 0.0

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
            mat = NifFormat.InertiaMatrix()
            mat.m11 = self.m11
            mat.m12 = self.m12
            mat.m13 = self.m13
            mat.m14 = self.m14
            mat.m21 = self.m21
            mat.m22 = self.m22
            mat.m23 = self.m23
            mat.m24 = self.m24
            mat.m31 = self.m31
            mat.m32 = self.m32
            mat.m33 = self.m33
            mat.m34 = self.m34
            return mat

        def __eq__(self, mat):
            if not isinstance(mat, NifFormat.InertiaMatrix):
                raise TypeError(
                    "do not know how to compare InertiaMatrix and %s"%mat.__class__)
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

    class LimitedHingeDescriptor:
        def updateAB(self, transform):
            """Update B pivot and axes from A using the given transform."""
            # pivot point
            pivotB = ((7 * self.pivotA.getVector3()) * transform) / 7.0
            self.pivotB.x = pivotB.x
            self.pivotB.y = pivotB.y
            self.pivotB.z = pivotB.z
            # axes (rotation only)
            transform = transform.getMatrix33()
            axleB = self.axleA.getVector3() *  transform
            perp2AxleInB2 = self.perp2AxleInA2.getVector3() * transform
            self.axleB.x = axleB.x
            self.axleB.y = axleB.y
            self.axleB.z = axleB.z
            self.perp2AxleInB2.x = perp2AxleInB2.x
            self.perp2AxleInB2.y = perp2AxleInB2.y
            self.perp2AxleInB2.z = perp2AxleInB2.z

    class Matrix44:
        def asList(self):
            """Return matrix as 4x4 list."""
            return [
                [self.m11, self.m12, self.m13, self.m14],
                [self.m21, self.m22, self.m23, self.m24],
                [self.m31, self.m32, self.m33, self.m34],
                [self.m41, self.m42, self.m43, self.m44]
                ]

        def asTuple(self):
            """Return matrix as 4x4 tuple."""
            return (
                (self.m11, self.m12, self.m13, self.m14),
                (self.m21, self.m22, self.m23, self.m24),
                (self.m31, self.m32, self.m33, self.m34),
                (self.m41, self.m42, self.m43, self.m44)
                )

        def setRows(self, row0, row1, row2, row3):
            """Set matrix from rows."""
            self.m11, self.m12, self.m13, self.m14 = row0
            self.m21, self.m22, self.m23, self.m24 = row1
            self.m31, self.m32, self.m33, self.m34 = row2
            self.m41, self.m42, self.m43, self.m44 = row3

        def __str__(self):
            return(
                "[ %6.3f %6.3f %6.3f %6.3f ]\n"
                "[ %6.3f %6.3f %6.3f %6.3f ]\n"
                "[ %6.3f %6.3f %6.3f %6.3f ]\n"
                "[ %6.3f %6.3f %6.3f %6.3f ]\n"
                % (self.m11, self.m12, self.m13, self.m14,
                   self.m21, self.m22, self.m23, self.m24,
                   self.m31, self.m32, self.m33, self.m34,
                   self.m41, self.m42, self.m43, self.m44))

        def setIdentity(self):
            """Set to identity matrix."""
            self.m11 = 1.0
            self.m12 = 0.0
            self.m13 = 0.0
            self.m14 = 0.0
            self.m21 = 0.0
            self.m22 = 1.0
            self.m23 = 0.0
            self.m24 = 0.0
            self.m31 = 0.0
            self.m32 = 0.0
            self.m33 = 1.0
            self.m34 = 0.0
            self.m41 = 0.0
            self.m42 = 0.0
            self.m43 = 0.0
            self.m44 = 1.0

        def isIdentity(self):
            """Return ``True`` if the matrix is close to identity."""
            if (abs(self.m11 - 1.0) > NifFormat._EPSILON
                or abs(self.m12) > NifFormat._EPSILON
                or abs(self.m13) > NifFormat._EPSILON
                or abs(self.m14) > NifFormat._EPSILON
                or abs(self.m21) > NifFormat._EPSILON
                or abs(self.m22 - 1.0) > NifFormat._EPSILON
                or abs(self.m23) > NifFormat._EPSILON
                or abs(self.m24) > NifFormat._EPSILON
                or abs(self.m31) > NifFormat._EPSILON
                or abs(self.m32) > NifFormat._EPSILON
                or abs(self.m33 - 1.0) > NifFormat._EPSILON
                or abs(self.m34) > NifFormat._EPSILON
                or abs(self.m41) > NifFormat._EPSILON
                or abs(self.m42) > NifFormat._EPSILON
                or abs(self.m43) > NifFormat._EPSILON
                or abs(self.m44 - 1.0) > NifFormat._EPSILON):
                return False
            else:
                return True

        def getCopy(self):
            """Create a copy of the matrix."""
            mat = NifFormat.Matrix44()
            mat.m11 = self.m11
            mat.m12 = self.m12
            mat.m13 = self.m13
            mat.m14 = self.m14
            mat.m21 = self.m21
            mat.m22 = self.m22
            mat.m23 = self.m23
            mat.m24 = self.m24
            mat.m31 = self.m31
            mat.m32 = self.m32
            mat.m33 = self.m33
            mat.m34 = self.m34
            mat.m41 = self.m41
            mat.m42 = self.m42
            mat.m43 = self.m43
            mat.m44 = self.m44
            return mat

        def getMatrix33(self):
            """Returns upper left 3x3 part."""
            m = NifFormat.Matrix33()
            m.m11 = self.m11
            m.m12 = self.m12
            m.m13 = self.m13
            m.m21 = self.m21
            m.m22 = self.m22
            m.m23 = self.m23
            m.m31 = self.m31
            m.m32 = self.m32
            m.m33 = self.m33
            return m

        def setMatrix33(self, m):
            """Sets upper left 3x3 part."""
            if not isinstance(m, NifFormat.Matrix33):
                raise TypeError('argument must be Matrix33')
            self.m11 = m.m11
            self.m12 = m.m12
            self.m13 = m.m13
            self.m21 = m.m21
            self.m22 = m.m22
            self.m23 = m.m23
            self.m31 = m.m31
            self.m32 = m.m32
            self.m33 = m.m33

        def getTranslation(self):
            """Returns lower left 1x3 part."""
            t = NifFormat.Vector3()
            t.x = self.m41
            t.y = self.m42
            t.z = self.m43
            return t

        def setTranslation(self, translation):
            """Returns lower left 1x3 part."""
            if not isinstance(translation, NifFormat.Vector3):
                raise TypeError('argument must be Vector3')
            self.m41 = translation.x
            self.m42 = translation.y
            self.m43 = translation.z

        def isScaleRotationTranslation(self):
            if not self.getMatrix33().isScaleRotation(): return False
            if abs(self.m14) > NifFormat._EPSILON: return False
            if abs(self.m24) > NifFormat._EPSILON: return False
            if abs(self.m34) > NifFormat._EPSILON: return False
            if abs(self.m44 - 1.0) > NifFormat._EPSILON: return False
            return True

        def getScaleRotationTranslation(self):
            rotscl = self.getMatrix33()
            scale = rotscl.getScale()
            rot = rotscl / scale
            trans = self.getTranslation()
            return (scale, rot, trans)

        def getScaleQuatTranslation(self):
            rotscl = self.getMatrix33()
            scale, quat = rotscl.getScaleQuat()
            trans = self.getTranslation()
            return (scale, quat, trans)

        def setScaleRotationTranslation(self, scale, rotation, translation):
            if not isinstance(scale, (float, int, long)):
                raise TypeError('scale must be float')
            if not isinstance(rotation, NifFormat.Matrix33):
                raise TypeError('rotation must be Matrix33')
            if not isinstance(translation, NifFormat.Vector3):
                raise TypeError('translation must be Vector3')

            if not rotation.isRotation():
                logger = logging.getLogger("pyffi.nif.matrix")
                mat = rotation * rotation.getTranspose()
                idmat = NifFormat.Matrix33()
                idmat.setIdentity()
                error = (mat - idmat).supNorm()
                logger.warning("improper rotation matrix (error is %f)" % error)
                logger.debug("  matrix =")
                for line in str(rotation).split("\n"):
                    logger.debug("    %s" % line)
                logger.debug("  its determinant = %f" % rotation.getDeterminant())
                logger.debug("  matrix * matrix^T =")
                for line in str(mat).split("\n"):
                    logger.debug("    %s" % line)

            self.m14 = 0.0
            self.m24 = 0.0
            self.m34 = 0.0
            self.m44 = 1.0

            self.setMatrix33(rotation * scale)
            self.setTranslation(translation)

        def getInverse(self, fast=True):
            """Calculates inverse (fast assumes isScaleRotationTranslation is True)."""
            def adjoint(m, ii, jj):
                result = []
                for i, row in enumerate(m):
                    if i == ii: continue
                    result.append([])
                    for j, x in enumerate(row):
                        if j == jj: continue
                        result[-1].append(x)
                return result
            def determinant(m):
                if len(m) == 2:
                    return m[0][0]*m[1][1] - m[1][0]*m[0][1]
                result = 0.0
                for i in xrange(len(m)):
                    det = determinant(adjoint(m, i, 0))
                    if i & 1:
                        result -= m[i][0] * det
                    else:
                        result += m[i][0] * det
                return result

            if fast:
                m = self.getMatrix33().getInverse()
                t = -(self.getTranslation() * m)

                n = NifFormat.Matrix44()
                n.m14 = 0.0
                n.m24 = 0.0
                n.m34 = 0.0
                n.m44 = 1.0
                n.setMatrix33(m)
                n.setTranslation(t)
                return n
            else:
                m = self.asList()
                nn = [[0.0 for i in xrange(4)] for j in xrange(4)]
                det = determinant(m)
                if abs(det) < NifFormat._EPSILON:
                    raise ZeroDivisionError('cannot invert matrix:\n%s'%self)
                for i in xrange(4):
                    for j in xrange(4):
                        if (i+j) & 1:
                            nn[j][i] = -determinant(adjoint(m, i, j)) / det
                        else:
                            nn[j][i] = determinant(adjoint(m, i, j)) / det
                n = NifFormat.Matrix44()
                n.setRows(*nn)
                return n

        def __mul__(self, x):
            if isinstance(x, (float, int, long)):
                m = NifFormat.Matrix44()
                m.m11 = self.m11 * x
                m.m12 = self.m12 * x
                m.m13 = self.m13 * x
                m.m14 = self.m14 * x
                m.m21 = self.m21 * x
                m.m22 = self.m22 * x
                m.m23 = self.m23 * x
                m.m24 = self.m24 * x
                m.m31 = self.m31 * x
                m.m32 = self.m32 * x
                m.m33 = self.m33 * x
                m.m34 = self.m34 * x
                m.m41 = self.m41 * x
                m.m42 = self.m42 * x
                m.m43 = self.m43 * x
                m.m44 = self.m44 * x
                return m
            elif isinstance(x, NifFormat.Vector3):
                raise TypeError("matrix*vector not supported; please use left multiplication (vector*matrix)")
            elif isinstance(x, NifFormat.Vector4):
                raise TypeError("matrix*vector not supported; please use left multiplication (vector*matrix)")
            elif isinstance(x, NifFormat.Matrix44):
                m = NifFormat.Matrix44()
                m.m11 = self.m11 * x.m11  +  self.m12 * x.m21  +  self.m13 * x.m31  +  self.m14 * x.m41
                m.m12 = self.m11 * x.m12  +  self.m12 * x.m22  +  self.m13 * x.m32  +  self.m14 * x.m42
                m.m13 = self.m11 * x.m13  +  self.m12 * x.m23  +  self.m13 * x.m33  +  self.m14 * x.m43
                m.m14 = self.m11 * x.m14  +  self.m12 * x.m24  +  self.m13 * x.m34  +  self.m14 * x.m44
                m.m21 = self.m21 * x.m11  +  self.m22 * x.m21  +  self.m23 * x.m31  +  self.m24 * x.m41
                m.m22 = self.m21 * x.m12  +  self.m22 * x.m22  +  self.m23 * x.m32  +  self.m24 * x.m42
                m.m23 = self.m21 * x.m13  +  self.m22 * x.m23  +  self.m23 * x.m33  +  self.m24 * x.m43
                m.m24 = self.m21 * x.m14  +  self.m22 * x.m24  +  self.m23 * x.m34  +  self.m24 * x.m44
                m.m31 = self.m31 * x.m11  +  self.m32 * x.m21  +  self.m33 * x.m31  +  self.m34 * x.m41
                m.m32 = self.m31 * x.m12  +  self.m32 * x.m22  +  self.m33 * x.m32  +  self.m34 * x.m42
                m.m33 = self.m31 * x.m13  +  self.m32 * x.m23  +  self.m33 * x.m33  +  self.m34 * x.m43
                m.m34 = self.m31 * x.m14  +  self.m32 * x.m24  +  self.m33 * x.m34  +  self.m34 * x.m44
                m.m41 = self.m41 * x.m11  +  self.m42 * x.m21  +  self.m43 * x.m31  +  self.m44 * x.m41
                m.m42 = self.m41 * x.m12  +  self.m42 * x.m22  +  self.m43 * x.m32  +  self.m44 * x.m42
                m.m43 = self.m41 * x.m13  +  self.m42 * x.m23  +  self.m43 * x.m33  +  self.m44 * x.m43
                m.m44 = self.m41 * x.m14  +  self.m42 * x.m24  +  self.m43 * x.m34  +  self.m44 * x.m44
                return m
            else:
                raise TypeError("do not know how to multiply Matrix44 with %s"%x.__class__)

        def __div__(self, x):
            if isinstance(x, (float, int, long)):
                m = NifFormat.Matrix44()
                m.m11 = self.m11 / x
                m.m12 = self.m12 / x
                m.m13 = self.m13 / x
                m.m14 = self.m14 / x
                m.m21 = self.m21 / x
                m.m22 = self.m22 / x
                m.m23 = self.m23 / x
                m.m24 = self.m24 / x
                m.m31 = self.m31 / x
                m.m32 = self.m32 / x
                m.m33 = self.m33 / x
                m.m34 = self.m34 / x
                m.m41 = self.m41 / x
                m.m42 = self.m42 / x
                m.m43 = self.m43 / x
                m.m44 = self.m44 / x
                return m
            else:
                raise TypeError("do not know how to divide Matrix44 by %s"%x.__class__)

        def __rmul__(self, x):
            if isinstance(x, (float, int, long)):
                return self * x
            else:
                raise TypeError("do not know how to multiply %s with Matrix44"%x.__class__)

        def __eq__(self, m):
            if isinstance(m, type(None)):
                return False
            if not isinstance(m, NifFormat.Matrix44):
                raise TypeError("do not know how to compare Matrix44 and %s"%m.__class__)
            if abs(self.m11 - m.m11) > NifFormat._EPSILON: return False
            if abs(self.m12 - m.m12) > NifFormat._EPSILON: return False
            if abs(self.m13 - m.m13) > NifFormat._EPSILON: return False
            if abs(self.m14 - m.m14) > NifFormat._EPSILON: return False
            if abs(self.m21 - m.m21) > NifFormat._EPSILON: return False
            if abs(self.m22 - m.m22) > NifFormat._EPSILON: return False
            if abs(self.m23 - m.m23) > NifFormat._EPSILON: return False
            if abs(self.m24 - m.m24) > NifFormat._EPSILON: return False
            if abs(self.m31 - m.m31) > NifFormat._EPSILON: return False
            if abs(self.m32 - m.m32) > NifFormat._EPSILON: return False
            if abs(self.m33 - m.m33) > NifFormat._EPSILON: return False
            if abs(self.m34 - m.m34) > NifFormat._EPSILON: return False
            if abs(self.m41 - m.m41) > NifFormat._EPSILON: return False
            if abs(self.m42 - m.m42) > NifFormat._EPSILON: return False
            if abs(self.m43 - m.m43) > NifFormat._EPSILON: return False
            if abs(self.m44 - m.m44) > NifFormat._EPSILON: return False
            return True

        def __ne__(self, m):
            return not self.__eq__(m)

        def __add__(self, x):
            if isinstance(x, (NifFormat.Matrix44)):
                m = NifFormat.Matrix44()
                m.m11 = self.m11 + x.m11
                m.m12 = self.m12 + x.m12
                m.m13 = self.m13 + x.m13
                m.m14 = self.m14 + x.m14
                m.m21 = self.m21 + x.m21
                m.m22 = self.m22 + x.m22
                m.m23 = self.m23 + x.m23
                m.m24 = self.m24 + x.m24
                m.m31 = self.m31 + x.m31
                m.m32 = self.m32 + x.m32
                m.m33 = self.m33 + x.m33
                m.m34 = self.m34 + x.m34
                m.m41 = self.m41 + x.m41
                m.m42 = self.m42 + x.m42
                m.m43 = self.m43 + x.m43
                m.m44 = self.m44 + x.m44
                return m
            elif isinstance(x, (int, long, float)):
                m = NifFormat.Matrix44()
                m.m11 = self.m11 + x
                m.m12 = self.m12 + x
                m.m13 = self.m13 + x
                m.m14 = self.m14 + x
                m.m21 = self.m21 + x
                m.m22 = self.m22 + x
                m.m23 = self.m23 + x
                m.m24 = self.m24 + x
                m.m31 = self.m31 + x
                m.m32 = self.m32 + x
                m.m33 = self.m33 + x
                m.m34 = self.m34 + x
                m.m41 = self.m41 + x
                m.m42 = self.m42 + x
                m.m43 = self.m43 + x
                m.m44 = self.m44 + x
                return m
            else:
                raise TypeError("do not know how to add Matrix44 and %s"%x.__class__)

        def __sub__(self, x):
            if isinstance(x, (NifFormat.Matrix44)):
                m = NifFormat.Matrix44()
                m.m11 = self.m11 - x.m11
                m.m12 = self.m12 - x.m12
                m.m13 = self.m13 - x.m13
                m.m14 = self.m14 - x.m14
                m.m21 = self.m21 - x.m21
                m.m22 = self.m22 - x.m22
                m.m23 = self.m23 - x.m23
                m.m24 = self.m24 - x.m24
                m.m31 = self.m31 - x.m31
                m.m32 = self.m32 - x.m32
                m.m33 = self.m33 - x.m33
                m.m34 = self.m34 - x.m34
                m.m41 = self.m41 - x.m41
                m.m42 = self.m42 - x.m42
                m.m43 = self.m43 - x.m43
                m.m44 = self.m44 - x.m44
                return m
            elif isinstance(x, (int, long, float)):
                m = NifFormat.Matrix44()
                m.m11 = self.m11 - x
                m.m12 = self.m12 - x
                m.m13 = self.m13 - x
                m.m14 = self.m14 - x
                m.m21 = self.m21 - x
                m.m22 = self.m22 - x
                m.m23 = self.m23 - x
                m.m24 = self.m24 - x
                m.m31 = self.m31 - x
                m.m32 = self.m32 - x
                m.m33 = self.m33 - x
                m.m34 = self.m34 - x
                m.m41 = self.m41 - x
                m.m42 = self.m42 - x
                m.m43 = self.m43 - x
                m.m44 = self.m44 - x
                return m
            else:
                raise TypeError("do not know how to substract Matrix44 and %s"
                                % x.__class__)

        def supNorm(self):
            """Calculate supremum norm of matrix (maximum absolute value of all
            entries)."""
            return max(max(abs(elem) for elem in row)
                       for row in self.asList())

    class NiAVObject:
        """
        Properties
        ==========

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> node = NifFormat.NiNode()
        >>> prop1 = NifFormat.NiProperty()
        >>> prop1.name = "hello"
        >>> prop2 = NifFormat.NiProperty()
        >>> prop2.name = "world"
        >>> node.getProperties()
        []
        >>> node.setProperties([prop1, prop2])
        >>> [prop.name for prop in node.getProperties()]
        ['hello', 'world']
        >>> [prop.name for prop in node.properties]
        ['hello', 'world']
        >>> node.setProperties([])
        >>> node.getProperties()
        []
        >>> # now set them the other way around
        >>> node.setProperties([prop2, prop1])
        >>> [prop.name for prop in node.getProperties()]
        ['world', 'hello']
        >>> [prop.name for prop in node.properties]
        ['world', 'hello']
        >>> node.removeProperty(prop2)
        >>> [prop.name for prop in node.properties]
        ['hello']
        >>> node.addProperty(prop2)
        >>> [prop.name for prop in node.properties]
        ['hello', 'world']
        """
        def addProperty(self, prop):
            """Add the given property to the property list.

            :param prop: The property block to add.
            :type prop: L{NifFormat.NiProperty}
            """
            num_props = self.numProperties
            self.numProperties = num_props + 1
            self.properties.updateSize()
            self.properties[num_props] = prop

        def removeProperty(self, prop):
            """Remove the given property to the property list.

            :param prop: The property block to remove.
            :type prop: L{NifFormat.NiProperty}
            """
            self.setProperties([otherprop for otherprop in self.getProperties()
                                if not(otherprop is prop)])

        def getProperties(self):
            """Return a list of the properties of the block.

            :return: The list of properties.
            :rtype: ``list`` of L{NifFormat.NiProperty}
            """
            return [prop for prop in self.properties]

        def setProperties(self, proplist):
            """Set the list of properties from the given list (destroys existing list).

            :param proplist: The list of property blocks to set.
            :type proplist: ``list`` of L{NifFormat.NiProperty}
            """
            self.numProperties = len(proplist)
            self.properties.updateSize()
            for i, prop in enumerate(proplist):
                self.properties[i] = prop

        def getTransform(self, relative_to=None):
            """Return scale, rotation, and translation into a single 4x4
            matrix, relative to the C{relative_to} block (which should be
            another NiAVObject connecting to this block). If C{relative_to} is
            ``None``, then returns the transform stored in C{self}, or
            equivalently, the target is assumed to be the parent.

            :param relative_to: The block relative to which the transform must
                be calculated. If ``None``, the local transform is returned.
            """
            m = NifFormat.Matrix44()
            m.setScaleRotationTranslation(self.scale, self.rotation, self.translation)
            if not relative_to: return m
            # find chain from relative_to to self
            chain = relative_to.findChain(self, block_type = NifFormat.NiAVObject)
            if not chain:
                raise ValueError('cannot find a chain of NiAVObject blocks')
            # and multiply with all transform matrices (not including relative_to)
            for block in reversed(chain[1:-1]):
                m *= block.getTransform()
            return m

        def setTransform(self, m):
            """Set rotation, translation, and scale, from a 4x4 matrix.

            :param m: The matrix to which the transform should be set."""
            scale, rotation, translation = m.getScaleRotationTranslation()

            self.scale = scale

            self.rotation.m11 = rotation.m11
            self.rotation.m12 = rotation.m12
            self.rotation.m13 = rotation.m13
            self.rotation.m21 = rotation.m21
            self.rotation.m22 = rotation.m22
            self.rotation.m23 = rotation.m23
            self.rotation.m31 = rotation.m31
            self.rotation.m32 = rotation.m32
            self.rotation.m33 = rotation.m33

            self.translation.x = translation.x
            self.translation.y = translation.y
            self.translation.z = translation.z

        def applyScale(self, scale):
            """Apply scale factor on data.

            :param scale: The scale factor."""
            # apply scale on translation
            self.translation.x *= scale
            self.translation.y *= scale
            self.translation.z *= scale
            # apply scale on bounding box
            self.boundingBox.translation.x *= scale
            self.boundingBox.translation.y *= scale
            self.boundingBox.translation.z *= scale
            self.boundingBox.radius.x *= scale
            self.boundingBox.radius.y *= scale
            self.boundingBox.radius.z *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

    class NiBSplineCompTransformInterpolator:
        def getTranslations(self):
            """Return an iterator over all translation keys."""
            return self._getCompKeys(self.translationOffset, 3,
                                     self.translationBias, self.translationMultiplier)

        def getRotations(self):
            """Return an iterator over all rotation keys."""
            return self._getCompKeys(self.rotationOffset, 4,
                                     self.rotationBias, self.rotationMultiplier)

        def getScales(self):
            """Return an iterator over all scale keys."""
            for key in self._getCompKeys(self.scaleOffset, 1,
                                         self.scaleBias, self.scaleMultiplier):
                yield key[0]

        def applyScale(self, scale):
            """Apply scale factor on data."""
            self.translation.x *= scale
            self.translation.y *= scale
            self.translation.z *= scale
            self.translationBias *= scale
            self.translationMultiplier *= scale

    class NiBSplineData:
        """
        >>> # a doctest
        >>> from PyFFI.Formats.NIF import NifFormat
        >>> block = NifFormat.NiBSplineData()
        >>> block.numShortControlPoints = 50
        >>> block.shortControlPoints.updateSize()
        >>> for i in xrange(block.numShortControlPoints):
        ...     block.shortControlPoints[i] = 20 - i
        >>> list(block.getShortData(12, 4, 3))
        [(8, 7, 6), (5, 4, 3), (2, 1, 0), (-1, -2, -3)]
        >>> offset = block.appendShortData([(1,2),(4,3),(13,14),(8,2),(33,33)])
        >>> offset
        50
        >>> list(block.getShortData(offset, 5, 2))
        [(1, 2), (4, 3), (13, 14), (8, 2), (33, 33)]
        >>> list(block.getCompData(offset, 5, 2, 10.0, 32767.0))
        [(11.0, 12.0), (14.0, 13.0), (23.0, 24.0), (18.0, 12.0), (43.0, 43.0)]
        >>> block.appendFloatData([(1.0,2.0),(3.0,4.0),(0.5,0.25)])
        0
        >>> list(block.getFloatData(0, 3, 2))
        [(1.0, 2.0), (3.0, 4.0), (0.5, 0.25)]
        >>> block.appendCompData([(1,2),(4,3)])
        (60, 2.5, 1.5)
        >>> list(block.getShortData(60, 2, 2))
        [(-32767, -10922), (32767, 10922)]
        >>> list(block.getCompData(60, 2, 2, 2.5, 1.5)) # doctest: +ELLIPSIS
        [(1.0, 2.00...), (4.0, 2.99...)]
        """
        def _getData(self, offset, num_elements, element_size, controlpoints):
            """Helper function for getFloatData and getShortData. For internal
            use only."""
            # check arguments
            if not (controlpoints is self.floatControlPoints
                    or controlpoints is self.shortControlPoints):
                raise ValueError("internal error while appending data")
            # parse the data
            for element in xrange(num_elements):
                yield tuple(
                    controlpoints[offset + element * element_size + index]
                    for index in xrange(element_size))

        def _appendData(self, data, controlpoints):
            """Helper function for appendFloatData and appendShortData. For internal
            use only."""
            # get number of elements
            num_elements = len(data)
            # empty list, do nothing
            if num_elements == 0:
                return
            # get element size
            element_size = len(data[0])
            # store offset at which we append the data
            if controlpoints is self.floatControlPoints:
                offset = self.numFloatControlPoints
                self.numFloatControlPoints += num_elements * element_size
            elif controlpoints is self.shortControlPoints:
                offset = self.numShortControlPoints
                self.numShortControlPoints += num_elements * element_size
            else:
                raise ValueError("internal error while appending data")
            # update size
            controlpoints.updateSize()
            # store the data
            for element, datum in enumerate(data):
                for index, value in enumerate(datum):
                    controlpoints[offset + element * element_size + index] = value
            # return the offset
            return offset

        def getShortData(self, offset, num_elements, element_size):
            """Get an iterator to the data.

            :param offset: The offset in the data where to start.
            :param num_elements: Number of elements to get.
            :param element_size: Size of a single element.
            :return: A list of C{num_elements} tuples of size C{element_size}.
            """
            return self._getData(
                offset, num_elements, element_size, self.shortControlPoints)

        def getCompData(self, offset, num_elements, element_size, bias, multiplier):
            """Get an interator to the data, converted to float with extra bias and
            multiplication factor. If C{x} is the short value, then the returned value
            is C{bias + x * multiplier / 32767.0}.

            :param offset: The offset in the data where to start.
            :param num_elements: Number of elements to get.
            :param element_size: Size of a single element.
            :param bias: Value bias.
            :param multiplier: Value multiplier.
            :return: A list of C{num_elements} tuples of size C{element_size}.
            """
            for key in self.getShortData(offset, num_elements, element_size):
                yield tuple(bias + x * multiplier / 32767.0 for x in key)

        def appendShortData(self, data):
            """Append data.

            :param data: A list of elements, where each element is a tuple of
                integers. (Note: cannot be an interator; maybe this restriction
                will be removed in a future version.)
            :return: The offset at which the data was appended."""
            return self._appendData(data, self.shortControlPoints)

        def appendCompData(self, data):
            """Append data as compressed list.

            :param data: A list of elements, where each element is a tuple of
                integers. (Note: cannot be an interator; maybe this restriction
                will be removed in a future version.)
            :return: The offset, bias, and multiplier."""
            # get extremes
            maxvalue = max(max(datum) for datum in data)
            minvalue = min(min(datum) for datum in data)
            # get bias and multiplier
            bias = 0.5 * (maxvalue + minvalue)
            if maxvalue > minvalue:
                multiplier = 0.5 * (maxvalue - minvalue)
            else:
                # no need to compress in this case
                multiplier = 1.0

            # compress points into shorts
            shortdata = []
            for datum in data:
                shortdata.append(tuple(int(32767 * (x - bias) / multiplier)
                                       for x in datum))
            return (self._appendData(shortdata, self.shortControlPoints),
                    bias, multiplier)

        def getFloatData(self, offset, num_elements, element_size):
            """Get an iterator to the data.

            :param offset: The offset in the data where to start.
            :param num_elements: Number of elements to get.
            :param element_size: Size of a single element.
            :return: A list of C{num_elements} tuples of size C{element_size}.
            """
            return self._getData(
                offset, num_elements, element_size, self.floatControlPoints)

        def appendFloatData(self, data):
            """Append data.

            :param data: A list of elements, where each element is a tuple of
                floats. (Note: cannot be an interator; maybe this restriction
                will be removed in a future version.)
            :return: The offset at which the data was appended."""
            return self._appendData(data, self.floatControlPoints)

    class NiBSplineInterpolator:
        def getTimes(self):
            """Return an iterator over all key times.

            @todo: When code for calculating the bsplines is ready, this function
            will return exactly self.basisData.numControlPoints - 1 time points, and
            not self.basisData.numControlPoints as it is now.
            """
            for i in xrange(self.basisData.numControlPoints):
                yield self.startTime + (i * (self.stopTime - self.startTime)
                                        / (self.basisData.numControlPoints - 1))

        def _getFloatKeys(self, offset, element_size):
            """Helper function to get iterator to various keys. Internal use only."""
            # are there keys?
            if offset == 65535:
                return
            # yield all keys
            for key in self.splineData.getFloatData(offset,
                                                    self.basisData.numControlPoints,
                                                    element_size):
                yield key

        def _getCompKeys(self, offset, element_size, bias, multiplier):
            """Helper function to get iterator to various keys. Internal use only."""
            # are there keys?
            if offset == 65535:
                return
            # yield all keys
            for key in self.splineData.getCompData(offset,
                                                   self.basisData.numControlPoints,
                                                   element_size,
                                                   bias, multiplier):
                yield key

    class NiBSplineTransformInterpolator:
        def getTranslations(self):
            """Return an iterator over all translation keys."""
            return self._getFloatKeys(self.translationOffset, 3)

        def getRotations(self):
            """Return an iterator over all rotation keys."""
            return self._getFloatKeys(self.rotationOffset, 4)

        def getScales(self):
            """Return an iterator over all scale keys."""
            for key in self._getFloatKeys(self.scaleOffset, 1):
                yield key[0]

        def applyScale(self, scale):
            """Apply scale factor on data."""
            self.translation.x *= scale
            self.translation.y *= scale
            self.translation.z *= scale
            # also scale translation float keys
            if self.translationOffset != 65535:
                offset = self.translationOffset
                num_elements = self.basisData.numControlPoints
                element_size = 3
                controlpoints = self.splineData.floatControlPoints
                for element in xrange(num_elements):
                    for index in xrange(element_size):
                        controlpoints[offset + element * element_size + index] *= scale

    class NiGeometryData:
        """
        >>> from PyFFI.Formats.NIF import NifFormat
        >>> geomdata = NifFormat.NiGeometryData()
        >>> geomdata.numVertices = 3
        >>> geomdata.hasVertices = True
        >>> geomdata.hasNormals = True
        >>> geomdata.hasVertexColors = True
        >>> geomdata.numUvSets = 2
        >>> geomdata.vertices.updateSize()
        >>> geomdata.normals.updateSize()
        >>> geomdata.vertexColors.updateSize()
        >>> geomdata.uvSets.updateSize()
        >>> geomdata.vertices[0].x = 1
        >>> geomdata.vertices[0].y = 2
        >>> geomdata.vertices[0].z = 3
        >>> geomdata.vertices[1].x = 4
        >>> geomdata.vertices[1].y = 5
        >>> geomdata.vertices[1].z = 6
        >>> geomdata.vertices[2].x = 1.200001
        >>> geomdata.vertices[2].y = 3.400001
        >>> geomdata.vertices[2].z = 5.600001
        >>> geomdata.normals[0].x = 0
        >>> geomdata.normals[0].y = 0
        >>> geomdata.normals[0].z = 1
        >>> geomdata.normals[1].x = 0
        >>> geomdata.normals[1].y = 1
        >>> geomdata.normals[1].z = 0
        >>> geomdata.normals[2].x = 1
        >>> geomdata.normals[2].y = 0
        >>> geomdata.normals[2].z = 0
        >>> geomdata.vertexColors[1].r = 0.310001
        >>> geomdata.vertexColors[1].g = 0.320001
        >>> geomdata.vertexColors[1].b = 0.330001
        >>> geomdata.vertexColors[1].a = 0.340001
        >>> geomdata.uvSets[0][0].u = 0.990001
        >>> geomdata.uvSets[0][0].v = 0.980001
        >>> geomdata.uvSets[0][2].u = 0.970001
        >>> geomdata.uvSets[0][2].v = 0.960001
        >>> geomdata.uvSets[1][0].v = 0.910001
        >>> geomdata.uvSets[1][0].v = 0.920001
        >>> geomdata.uvSets[1][2].v = 0.930001
        >>> geomdata.uvSets[1][2].v = 0.940001
        >>> for h in geomdata.getVertexHashGenerator():
        ...     print(h)
        (1000, 2000, 3000, 0, 0, 1000, 99000, 98000, 0, 92000, 0, 0, 0, 0)
        (4000, 5000, 6000, 0, 1000, 0, 0, 0, 0, 0, 310, 320, 330, 340)
        (1200, 3400, 5600, 1000, 0, 0, 97000, 96000, 0, 94000, 0, 0, 0, 0)
        """
        def updateCenterRadius(self):
            """Recalculate center and radius of the data."""
            # in case there are no vertices, set center and radius to zero
            if len(self.vertices) == 0:
                self.center.x = 0.0
                self.center.y = 0.0
                self.center.z = 0.0
                self.radius = 0.0
                return

            # find extreme values in x, y, and z direction
            lowx = min([v.x for v in self.vertices])
            lowy = min([v.y for v in self.vertices])
            lowz = min([v.z for v in self.vertices])
            highx = max([v.x for v in self.vertices])
            highy = max([v.y for v in self.vertices])
            highz = max([v.z for v in self.vertices])

            # center is in the center of the bounding box
            cx = (lowx + highx) * 0.5
            cy = (lowy + highy) * 0.5
            cz = (lowz + highz) * 0.5
            self.center.x = cx
            self.center.y = cy
            self.center.z = cz

            # radius is the largest distance from the center
            r2 = 0.0
            for v in self.vertices:
                dx = cx - v.x
                dy = cy - v.y
                dz = cz - v.z
                r2 = max(r2, dx*dx+dy*dy+dz*dz)
            self.radius = r2 ** 0.5

        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < NifFormat._EPSILON: return
            for v in self.vertices:
                v.x *= scale
                v.y *= scale
                v.z *= scale
            self.center.x *= scale
            self.center.y *= scale
            self.center.z *= scale
            self.radius *= scale

        def getVertexHashGenerator(self,
                                   vertexprecision=3, normalprecision=3,
                                   uvprecision=5, vcolprecision=3):
            """Generator which produces a tuple of integers for each
            (vertex, normal, uv, vcol), to ease detection of duplicate vertices.
            The precision parameters denote number of significant digits.

            Default for uvprecision is higher than default for the rest because
            for very large models the uv coordinates can be very close together.

            :param vertexprecision: Precision to be used for vertices.
            :type vertexprecision: float
            :param normalprecision: Precision to be used for normals.
            :type normalprecision: float
            :param uvprecision: Precision to be used for uvs.
            :type uvprecision: float
            :param vcolprecision: Precision to be used for vertex colors.
            :type vcolprecision: float
            :return: A generator yielding a hash value for each vertex.
            """
            verts = self.vertices if self.hasVertices else None
            norms = self.normals if self.hasNormals else None
            uvsets = self.uvSets if len(self.uvSets) else None
            vcols = self.vertexColors if self.hasVertexColors else None
            vertexfactor = 10 ** vertexprecision
            normalfactor = 10 ** normalprecision
            uvfactor = 10 ** uvprecision
            vcolfactor = 10 ** vcolprecision
            for i in xrange(self.numVertices):
                h = []
                if verts:
                    h.extend([int(x * vertexfactor)
                             for x in [verts[i].x, verts[i].y, verts[i].z]])
                if norms:
                    h.extend([int(x * normalfactor)
                              for x in [norms[i].x, norms[i].y, norms[i].z]])
                if uvsets:
                    for uvset in uvsets:
                        h.extend([int(x*uvfactor) for x in [uvset[i].u, uvset[i].v]])
                if vcols:
                    h.extend([int(x * vcolfactor)
                              for x in [vcols[i].r, vcols[i].g,
                                        vcols[i].b, vcols[i].a]])
                yield tuple(h)

    class NiGeometry:
        """
        >>> from PyFFI.Formats.NIF import NifFormat
        >>> id44 = NifFormat.Matrix44()
        >>> id44.setIdentity()
        >>> skelroot = NifFormat.NiNode()
        >>> skelroot.name = 'skelroot'
        >>> skelroot.setTransform(id44)
        >>> bone1 = NifFormat.NiNode()
        >>> bone1.name = 'bone1'
        >>> bone1.setTransform(id44)
        >>> bone2 = NifFormat.NiNode()
        >>> bone2.name = 'bone2'
        >>> bone2.setTransform(id44)
        >>> bone21 = NifFormat.NiNode()
        >>> bone21.name = 'bone21'
        >>> bone21.setTransform(id44)
        >>> bone22 = NifFormat.NiNode()
        >>> bone22.name = 'bone22'
        >>> bone22.setTransform(id44)
        >>> bone211 = NifFormat.NiNode()
        >>> bone211.name = 'bone211'
        >>> bone211.setTransform(id44)
        >>> skelroot.addChild(bone1)
        >>> bone1.addChild(bone2)
        >>> bone2.addChild(bone21)
        >>> bone2.addChild(bone22)
        >>> bone21.addChild(bone211)
        >>> geom = NifFormat.NiTriShape()
        >>> geom.name = 'geom'
        >>> geom.setTransform(id44)
        >>> geomdata = NifFormat.NiTriShapeData()
        >>> skininst = NifFormat.NiSkinInstance()
        >>> skindata = NifFormat.NiSkinData()
        >>> skelroot.addChild(geom)
        >>> geom.data = geomdata
        >>> geom.skinInstance = skininst
        >>> skininst.skeletonRoot = skelroot
        >>> skininst.data = skindata
        >>> skininst.numBones = 4
        >>> skininst.bones.updateSize()
        >>> skininst.bones[0] = bone1
        >>> skininst.bones[1] = bone2
        >>> skininst.bones[2] = bone22
        >>> skininst.bones[3] = bone211
        >>> skindata.numBones = 4
        >>> skindata.boneList.updateSize()
        >>> [child.name for child in skelroot.children]
        ['bone1', 'geom']
        >>> skindata.setTransform(id44)
        >>> for bonedata in skindata.boneList:
        ...     bonedata.setTransform(id44)
        >>> affectedbones = geom.flattenSkin()
        >>> [bone.name for bone in affectedbones]
        ['bone1', 'bone2', 'bone22', 'bone211']
        >>> [child.name for child in skelroot.children]
        ['geom', 'bone1', 'bone21', 'bone2', 'bone22', 'bone211']
        """
        def isSkin(self):
            """Returns True if geometry is skinned."""
            return self.skinInstance != None

        def _validateSkin(self):
            """Check that skinning blocks are valid. Will raise NifError exception
            if not."""
            if self.skinInstance == None: return
            if self.skinInstance.data == None:
                raise NifFormat.NifError('NiGeometry has NiSkinInstance without NiSkinData')
            if self.skinInstance.skeletonRoot == None:
                raise NifFormat.NifError('NiGeometry has NiSkinInstance without skeleton root')
            if self.skinInstance.numBones != self.skinInstance.data.numBones:
                raise NifFormat.NifError('NiSkinInstance and NiSkinData have different number of bones')

        def addBone(self, bone, vert_weights):
            """Add bone with given vertex weights.
            After adding all bones, the geometry skinning information should be set
            from the current position of the bones using the L{updateBindPosition} function.

            :param bone: The bone NiNode block.
            :param vert_weights: A dictionary mapping each influenced vertex index to a vertex weight."""
            self._validateSkin()
            skininst = self.skinInstance
            skindata = skininst.data
            skelroot = skininst.skeletonRoot

            bone_index = skininst.numBones
            skininst.numBones = bone_index+1
            skininst.bones.updateSize()
            skininst.bones[bone_index] = bone
            skindata.numBones = bone_index+1
            skindata.boneList.updateSize()
            skinbonedata = skindata.boneList[bone_index]
            # set vertex weights
            skinbonedata.numVertices = len(vert_weights)
            skinbonedata.vertexWeights.updateSize()
            for i, (vert_index, vert_weight) in enumerate(vert_weights.iteritems()):
                skinbonedata.vertexWeights[i].index = vert_index
                skinbonedata.vertexWeights[i].weight = vert_weight



        def getVertexWeights(self):
            """Get vertex weights in a convenient format: list bone and weight per
            vertex."""
            # shortcuts relevant blocks
            if not self.skinInstance:
                raise NifFormat.NifError('Cannot get vertex weights of geometry without skin.')
            self._validateSkin()
            geomdata = self.data
            skininst = self.skinInstance
            skindata = skininst.data
            weights = [[] for i in xrange(geomdata.numVertices)]
            for bonenum, bonedata in enumerate(skindata.boneList):
                for skinweight in bonedata.vertexWeights:
                    weights[skinweight.index].append([bonenum, skinweight.weight])
            return weights


        def flattenSkin(self):
            """Reposition all bone blocks and geometry block in the tree to be direct
            children of the skeleton root.

            Returns list of all used bones by the skin."""

            if not self.isSkin(): return [] # nothing to do

            result = [] # list of repositioned bones
            self._validateSkin() # validate the skin
            skininst = self.skinInstance
            skindata = skininst.data
            skelroot = skininst.skeletonRoot

            # reparent geometry
            self.setTransform(self.getTransform(skelroot))
            geometry_parent = skelroot.findChain(self, block_type = NifFormat.NiAVObject)[-2]
            geometry_parent.removeChild(self) # detatch geometry from tree
            skelroot.addChild(self, front = True) # and attatch it to the skeleton root

            # reparent all the bone blocks
            for bone_block in skininst.bones:
                # skeleton root, if it is used as bone, does not need to be processed
                if bone_block == skelroot: continue
                # get bone parent
                bone_parent = skelroot.findChain(bone_block, block_type = NifFormat.NiAVObject)[-2]
                # set new child transforms
                for child in bone_block.children:
                    child.setTransform(child.getTransform(bone_parent))
                # reparent children
                for child in bone_block.children:
                    bone_parent.addChild(child)
                bone_block.numChildren = 0
                bone_block.children.updateSize() # = removeChild on each child
                # set new bone transform
                bone_block.setTransform(bone_block.getTransform(skelroot))
                # reparent bone block
                bone_parent.removeChild(bone_block)
                skelroot.addChild(bone_block)
                result.append(bone_block)

            return result



        # The nif skinning algorithm works as follows (as of nifskope):
        # v'                               # vertex after skinning in geometry space
        # = sum over {b in skininst.bones} # sum over all bones b that influence the mesh
        # weight[v][b]                     # how much bone b influences vertex v
        # * v                              # vertex before skinning in geometry space (as it is stored in the shape data)
        # * skindata.boneList[b].transform # transform vertex to bone b space in the rest pose
        # * b.getTransform(skelroot)       # apply animation, by multiplying with all bone matrices in the chain down to the skeleton root; the vertex is now in skeleton root space
        # * skindata.transform             # transforms vertex from skeleton root space back to geometry space
        def getSkinDeformation(self):
            """Returns a list of vertices and normals in their final position after
            skinning, in geometry space."""

            if not self.data: return [], []

            if not self.isSkin(): return self.data.vertices, self.data.normals

            self._validateSkin()
            skininst = self.skinInstance
            skindata = skininst.data
            skelroot = skininst.skeletonRoot

            vertices = [ NifFormat.Vector3() for i in xrange(self.data.numVertices) ]
            normals = [ NifFormat.Vector3() for i in xrange(self.data.numVertices) ]
            sumweights = [ 0.0 for i in xrange(self.data.numVertices) ]
            skin_offset = skindata.getTransform()
            for i, bone_block in enumerate(skininst.bones):
                bonedata = skindata.boneList[i]
                bone_offset = bonedata.getTransform()
                bone_matrix = bone_block.getTransform(skelroot)
                transform = bone_offset * bone_matrix * skin_offset
                scale, rotation, translation = transform.getScaleRotationTranslation()
                for skinweight in bonedata.vertexWeights:
                    index = skinweight.index
                    weight = skinweight.weight
                    vertices[index] += weight * (self.data.vertices[index] * transform)
                    if self.data.hasNormals:
                        normals[index] += weight * (self.data.normals[index] * rotation)
                    sumweights[index] += weight

            for i, s in enumerate(sumweights):
                if abs(s - 1.0) > 0.01: 
                    logging.getLogger("pyffi.nif.nigeometry").warn(
                        "vertex %i has weights not summing to one" % i)

            return vertices, normals



        # ported and extended from niflib::NiNode::GoToSkeletonBindPosition() (r2518)
        def sendBonesToBindPosition(self):
            """Send all bones to their bind position.

            @deprecated: Use L{NifFormat.NiNode.sendBonesToBindPosition} instead of
                this function.
            """

            warnings.warn("use NifFormat.NiNode.sendBonesToBindPosition",
                          DeprecationWarning)

            if not self.isSkin():
                return

            # validate skin and set up quick links
            self._validateSkin()
            skininst = self.skinInstance
            skindata = skininst.data
            skelroot = skininst.skeletonRoot

            # reposition the bones
            for i, parent_bone in enumerate(skininst.bones):
                parent_offset = skindata.boneList[i].getTransform()
                # if parent_bone is a child of the skeleton root, then fix its
                # transfrom
                if parent_bone in skelroot.children:
                    parent_bone.setTransform(parent_offset.getInverse() * self.getTransform(skelroot))
                # fix the transform of all its children
                for j, child_bone in enumerate(skininst.bones):
                    if child_bone not in parent_bone.children: continue
                    child_offset = skindata.boneList[j].getTransform()
                    child_matrix = child_offset.getInverse() * parent_offset
                    child_bone.setTransform(child_matrix)



        # ported from niflib::NiSkinData::ResetOffsets (r2561)
        def updateBindPosition(self):
            """Make current position of the bones the bind position for this geometry.

            Sets the NiSkinData overall transform to the inverse of the geometry transform
            relative to the skeleton root, and sets the NiSkinData of each bone to
            the geometry transform relative to the skeleton root times the inverse of the bone
            transform relative to the skeleton root."""
            if not self.isSkin(): return

            # validate skin and set up quick links
            self._validateSkin()
            skininst = self.skinInstance
            skindata = skininst.data
            skelroot = skininst.skeletonRoot

            # calculate overall offset
            geomtransform = self.getTransform(skelroot)
            skindata.setTransform(geomtransform.getInverse())

            # calculate bone offsets
            for i, bone in enumerate(skininst.bones):
                 skindata.boneList[i].setTransform(geomtransform * bone.getTransform(skelroot).getInverse())

        def getSkinPartition(self):
            """Return the skin partition block."""
            skininst = self.skinInstance
            if not skininst:
                skinpart = None
            else:
                skinpart = skininst.skinPartition
                if not skinpart:
                    skindata = skininst.data
                    if skindata:
                        skinpart = skindata.skinPartition

            return skinpart

        def setSkinPartition(self, skinpart):
            """Set skin partition block."""
            skininst = self.skinInstance
            if not skininst:
                raise ValueError("Geometry has no skin instance.")

            skindata = skininst.data
            if not skindata:
                raise ValueError("Geometry has no skin data.")

            skininst.skinPartition = skinpart
            skindata.skinPartition = skinpart

    class NiKeyframeData:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            for key in self.translations.keys:
                key.value.x *= scale
                key.value.y *= scale
                key.value.z *= scale
                #key.forward.x *= scale
                #key.forward.y *= scale
                #key.forward.z *= scale
                #key.backward.x *= scale
                #key.backward.y *= scale
                #key.backward.z *= scale
                # what to do with TBC?

    class NiMorphData:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            for morph in self.morphs:
                for v in morph.vectors:
                    v.x *= scale
                    v.y *= scale
                    v.z *= scale

    class NiNode:
        """
        Doctests
        ========

        Old test code
        -------------

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> x = NifFormat.NiNode()
        >>> y = NifFormat.NiNode()
        >>> z = NifFormat.NiNode()
        >>> x.numChildren =1
        >>> x.children.updateSize()
        >>> y in x.children
        False
        >>> x.children[0] = y
        >>> y in x.children
        True
        >>> x.addChild(z, front = True)
        >>> x.addChild(y)
        >>> x.numChildren
        2
        >>> x.children[0] is z
        True
        >>> x.removeChild(y)
        >>> y in x.children
        False
        >>> x.numChildren
        1
        >>> e = NifFormat.NiSpotLight()
        >>> x.addEffect(e)
        >>> x.numEffects
        1
        >>> e in x.effects
        True

        Children
        --------

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> node = NifFormat.NiNode()
        >>> child1 = NifFormat.NiNode()
        >>> child1.name = "hello"
        >>> child2 = NifFormat.NiNode()
        >>> child2.name = "world"
        >>> node.getChildren()
        []
        >>> node.setChildren([child1, child2])
        >>> [child.name for child in node.getChildren()]
        ['hello', 'world']
        >>> [child.name for child in node.children]
        ['hello', 'world']
        >>> node.setChildren([])
        >>> node.getChildren()
        []
        >>> # now set them the other way around
        >>> node.setChildren([child2, child1])
        >>> [child.name for child in node.getChildren()]
        ['world', 'hello']
        >>> [child.name for child in node.children]
        ['world', 'hello']
        >>> node.removeChild(child2)
        >>> [child.name for child in node.children]
        ['hello']
        >>> node.addChild(child2)
        >>> [child.name for child in node.children]
        ['hello', 'world']

        Effects
        -------

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> node = NifFormat.NiNode()
        >>> effect1 = NifFormat.NiSpotLight()
        >>> effect1.name = "hello"
        >>> effect2 = NifFormat.NiSpotLight()
        >>> effect2.name = "world"
        >>> node.getEffects()
        []
        >>> node.setEffects([effect1, effect2])
        >>> [effect.name for effect in node.getEffects()]
        ['hello', 'world']
        >>> [effect.name for effect in node.effects]
        ['hello', 'world']
        >>> node.setEffects([])
        >>> node.getEffects()
        []
        >>> # now set them the other way around
        >>> node.setEffects([effect2, effect1])
        >>> [effect.name for effect in node.getEffects()]
        ['world', 'hello']
        >>> [effect.name for effect in node.effects]
        ['world', 'hello']
        >>> node.removeEffect(effect2)
        >>> [effect.name for effect in node.effects]
        ['hello']
        >>> node.addEffect(effect2)
        >>> [effect.name for effect in node.effects]
        ['hello', 'world']
        """
        def addChild(self, child, front=False):
            """Add block to child list.

            :param child: The child to add.
            :type child: L{NifFormat.NiAVObject}
            :keyword front: Whether to add to the front or to the end of the
                list (default is at end).
            :type front: ``bool``
            """
            # check if it's already a child
            if child in self.children:
                return
            # increase number of children
            num_children = self.numChildren
            self.numChildren = num_children + 1
            self.children.updateSize()
            # add the child
            if not front:
                self.children[num_children] = child
            else:
                for i in xrange(num_children, 0, -1):
                    self.children[i] = self.children[i-1]
                self.children[0] = child

        def removeChild(self, child):
            """Remove a block from the child list.

            :param child: The child to remove.
            :type child: L{NifFormat.NiAVObject}
            """
            self.setChildren([otherchild for otherchild in self.getChildren()
                              if not(otherchild is child)])

        def getChildren(self):
            """Return a list of the children of the block.

            :return: The list of children.
            :rtype: ``list`` of L{NifFormat.NiAVObject}
            """
            return [child for child in self.children]

        def setChildren(self, childlist):
            """Set the list of children from the given list (destroys existing list).

            :param childlist: The list of child blocks to set.
            :type childlist: ``list`` of L{NifFormat.NiAVObject}
            """
            self.numChildren = len(childlist)
            self.children.updateSize()
            for i, child in enumerate(childlist):
                self.children[i] = child

        def addEffect(self, effect):
            """Add an effect to the list of effects.

            :param effect: The effect to add.
            :type effect: L{NifFormat.NiDynamicEffect}
            """
            num_effs = self.numEffects
            self.numEffects = num_effs + 1
            self.effects.updateSize()
            self.effects[num_effs] = effect

        def removeEffect(self, effect):
            """Remove a block from the effect list.

            :param effect: The effect to remove.
            :type effect: L{NifFormat.NiDynamicEffect}
            """
            self.setEffects([othereffect for othereffect in self.getEffects()
                             if not(othereffect is effect)])

        def getEffects(self):
            """Return a list of the effects of the block.

            :return: The list of effects.
            :rtype: ``list`` of L{NifFormat.NiDynamicEffect}
            """
            return [effect for effect in self.effects]

        def setEffects(self, effectlist):
            """Set the list of effects from the given list (destroys existing list).

            :param effectlist: The list of effect blocks to set.
            :type effectlist: ``list`` of L{NifFormat.NiDynamicEffect}
            """
            self.numEffects = len(effectlist)
            self.effects.updateSize()
            for i, effect in enumerate(effectlist):
                self.effects[i] = effect

        def mergeExternalSkeletonRoot(self, skelroot):
            """Attach skinned geometry to self (which will be the new skeleton root of
            the nif at the given skeleton root). Use this function if you move a
            skinned geometry from one nif into a new nif file. The bone links will be
            updated to point to the tree at self, instead of to the external tree.
            """
            # sanity check
            if self.name != skelroot.name:
                raise ValueError("skeleton root names do not match")

            # get a dictionary mapping bone names to bone blocks
            bone_dict = {}
            for block in self.tree():
                if isinstance(block, NifFormat.NiNode):
                    if block.name:
                        if block.name in bone_dict:
                            raise ValueError(
                                "multiple NiNodes with name %s" % block.name)
                        bone_dict[block.name] = block

            # add all non-bone children of the skeleton root to self
            for child in skelroot.getChildren():
                # skip empty children
                if not child:
                    continue
                # skip bones
                if child.name in bone_dict:
                    continue
                # not a bone, so add it
                self.addChild(child)
                # fix links to skeleton root and bones
                for externalblock in child.tree():
                    if isinstance(externalblock, NifFormat.NiSkinInstance):
                        if not(externalblock.skeletonRoot is skelroot):
                            raise ValueError(
                                "expected skeleton root %s but got %s"
                                % (skelroot.name, externalblock.skeletonRoot.name))
                        externalblock.skeletonRoot = self
                        for i, externalbone in enumerate(externalblock.bones):
                            externalblock.bones[i] = bone_dict[externalbone.name]

        def mergeSkeletonRoots(self):
            """This function will look for other geometries whose skeleton
            root is a (possibly indirect) child of this node. It will then
            reparent those geometries to this node. For example, it will unify
            the skeleton roots in Morrowind's cliffracer.nif file, or of the
            (official) body skins. This makes it much easier to import
            skeletons in for instance Blender: there will be only one skeleton
            root for each bone, over all geometries.

            The merge fails for those geometries whose global skin data
            transform does not match the inverse geometry transform relative to
            the skeleton root (the maths does not work out in this case!)

            Returns list of all new blocks that have been reparented (and
            added to the skeleton root children list), and a list of blocks
            for which the merge failed.
            """
            logger = logging.getLogger("pyffi.nif.ninode")

            result = [] # list of reparented blocks
            failed = [] # list of blocks that could not be reparented

            id44 = NifFormat.Matrix44()
            id44.setIdentity()

            # find the root block (direct parent of skeleton root that connects to the geometry) for each of these geometries
            for geom in self.getGlobalIterator():
                # make sure we only do each geometry once
                if (geom in result) or (geom in failed):
                    continue
                # only geometries
                if not isinstance(geom, NifFormat.NiGeometry):
                    continue
                # only skins
                if not geom.isSkin():
                    continue
                # only if they have a different skeleton root
                if geom.skinInstance.skeletonRoot is self:
                    continue
                # check transforms
                if (geom.skinInstance.data.getTransform()
                    * geom.getTransform(geom.skinInstance.skeletonRoot) != id44):
                    logger.warn(
                        "can't rebase %s: global skin data transform does not match "
                        "geometry transform relative to skeleton root" % geom.name)
                    failed.append(geom)
                    continue # skip this one
                # everything ok!
                # find geometry parent
                geomroot = geom.skinInstance.skeletonRoot.findChain(geom)[-2]
                # reparent
                logger.debug("detaching %s from %s" % (geom.name, geomroot.name))
                geomroot.removeChild(geom)
                logger.debug("attaching %s to %s" % (geom.name, self.name))
                self.addChild(geom)
                # set its new skeleton root
                geom.skinInstance.skeletonRoot = self
                # fix transform
                geom.skinInstance.data.setTransform(
                    geom.getTransform(self).getInverse(fast=False))
                # and signal that we reparented this block
                result.append(geom)

            return result, failed

        def getSkinnedGeometries(self):
            """This function yields all skinned geometries which have self as
            skeleton root.
            """
            for geom in self.getGlobalIterator():
                if (isinstance(geom, NifFormat.NiGeometry)
                    and geom.isSkin()
                    and geom.skinInstance.skeletonRoot is self):
                    yield geom

        def sendGeometriesToBindPosition(self):
            """Call this on the skeleton root of geometries. This function will
            transform the geometries, such that all skin data transforms coincide, or
            at least coincide partially.

            :return: A number quantifying the remaining difference between bind
                positions.
            :rtype: C{float}
            """
            # get logger
            logger = logging.getLogger("pyffi.nif.ninode")
            # maps bone name to bind position transform matrix (relative to
            # skeleton root)
            bone_bind_transform = {}
            # find all skinned geometries with self as skeleton root
            geoms = list(self.getSkinnedGeometries())
            # sort geometries by bone level
            # this ensures that "parent" geometries serve as reference for "child"
            # geometries
            sorted_geoms = []
            for bone in self.getGlobalIterator():
                if not isinstance(bone, NifFormat.NiNode):
                    continue
                for geom in geoms:
                    if not geom in sorted_geoms:
                        if bone in geom.skinInstance.bones:
                            sorted_geoms.append(geom)
            geoms = sorted_geoms
            # now go over all geometries and synchronize their relative bind poses
            for geom in geoms:
                skininst = geom.skinInstance
                skindata = skininst.data
                # set difference matrix to identity
                diff = NifFormat.Matrix44()
                diff.setIdentity()
                # go over all bones in current geometry, see if it has been visited
                # before
                for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
                    if bonenode.name in bone_bind_transform:
                        # calculate difference
                        # (see explanation below)
                        diff = (bonedata.getTransform()
                                * bone_bind_transform[bonenode.name]
                                * geom.getTransform(self).getInverse(fast=False))
                        break

                if diff.isIdentity():
                    logger.debug("%s is already in bind position" % geom.name)
                else:
                    logger.info("fixing %s bind position" % geom.name)
                    # explanation:
                    # we must set the bonedata transform T' such that its bone bind
                    # position matrix
                    #   T'^-1 * G
                    # (where T' = the updated bonedata.getTransform()
                    # and G = geom.getTransform(self))
                    # coincides with the desired matrix
                    #   B = bone_bind_transform[bonenode.name]
                    # in other words:
                    #   T' = G * B^-1
                    # or, with diff = D = T * B * G^-1
                    #   T' = D^-1 * T
                    # to keep the geometry in sync, the vertices and normals must
                    # be multiplied with D, e.g. v' = v * D
                    # because the full transform
                    #    v * T * ... = v * D * D^-1 * T * ... = v' * T' * ...
                    # must be kept invariant
                    for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
                        logger.debug("transforming bind position of bone %s"
                                     % bonenode.name)
                        bonedata.setTransform(diff.getInverse(fast=False)
                                              * bonedata.getTransform())
                    # transform geometry
                    logger.debug("transforming vertices and normals")
                    for vert in geom.data.vertices:
                        newvert = vert * diff
                        vert.x = newvert.x
                        vert.y = newvert.y
                        vert.z = newvert.z
                    for norm in geom.data.normals:
                        newnorm = norm * diff.getMatrix33()
                        norm.x = newnorm.x
                        norm.y = newnorm.y
                        norm.z = newnorm.z

                # store updated bind position for future reference
                for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
                    bone_bind_transform[bonenode.name] = (
                        bonedata.getTransform().getInverse(fast=False)
                        * geom.getTransform(self))

            # validation: check that bones share bind position
            bone_bind_transform = {}
            error = 0.0
            for geom in geoms:
                skininst = geom.skinInstance
                skindata = skininst.data
                # go over all bones in current geometry, see if it has been visited
                # before
                for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
                    if bonenode.name in bone_bind_transform:
                        # calculate difference
                        diff = ((bonedata.getTransform().getInverse(fast=False)
                                 * geom.getTransform(self))
                                - bone_bind_transform[bonenode.name])
                        # calculate error (sup norm)
                        error = max(error,
                                    max(max(abs(elem) for elem in row)
                                        for row in diff.asList()))
                    else:
                        bone_bind_transform[bonenode.name] = (
                            bonedata.getTransform().getInverse(fast=False)
                            * geom.getTransform(self))

            logger.debug("Geometry bind position error is %f" % error)
            if error > 1e-3:
                logger.warning("Failed to send some geometries to bind position")
            return error

        def sendDetachedGeometriesToNodePosition(self):
            """Some nifs (in particular in Morrowind) have geometries that are skinned
            but that do not share bones. In such cases, sendGeometriesToBindPosition
            cannot reposition them. This function will send such geometries to the
            position of their root node.

            Examples of such nifs are the official Morrowind skins (after merging
            skeleton roots).

            Returns list of detached geometries that have been moved.
            """
            logger = logging.getLogger("pyffi.nif.ninode")
            geoms = list(self.getSkinnedGeometries())

            # parts the geometries into sets that do not share bone influences
            # * first construct sets of bones, merge intersecting sets
            # * then check which geometries belong to which set
            bonesets = [list(set(geom.skinInstance.bones)) for geom in geoms]
            # the merged flag signals that we are still merging bones
            merged = True
            while merged:
                merged = False
                for boneset in bonesets:
                    for other_boneset in bonesets:
                        # skip if sets are identical
                        if other_boneset is boneset:
                            continue
                        # if not identical, see if they can be merged
                        if set(other_boneset) & set(boneset):
                            # XXX hackish but works
                            # calculate union
                            updated_boneset = list(set(other_boneset) | set(boneset))
                            # and move all bones into one bone set
                            del other_boneset[:]
                            del boneset[:]
                            boneset += updated_boneset
                            merged = True
            # remove empty bone sets
            bonesets = list(boneset for boneset in bonesets if boneset)
            logger.debug("bones per partition are")
            for boneset in bonesets:
                logger.debug(str([bone.name for bone in boneset]))
            parts = [[geom for geom in geoms
                          if set(geom.skinInstance.bones) & set(boneset)]
                         for boneset in bonesets]
            logger.debug("geometries per partition are")
            for part in parts:
                logger.debug(str([geom.name for geom in part]))
            # if there is only one set, we are done
            if len(bonesets) <= 1:
                logger.debug("no detached geometries")
                return []

            # next, for each part, move all geometries so the lowest bone matches the
            # node transform
            for boneset, part in izip(bonesets, parts):
                logger.debug("moving part %s" % str([geom.name for geom in part]))
                # find "lowest" bone in the bone set
                lowest_dist = None
                lowest_bonenode = None
                for bonenode in boneset:
                    dist = len(self.findChain(bonenode))
                    if (lowest_dist is None) or (lowest_dist > dist):
                        lowest_dist = dist
                        lowest_bonenode = bonenode
                logger.debug("reference bone is %s" % lowest_bonenode.name)
                # find a geometry that has this bone
                for geom in part:
                    for bonenode, bonedata in izip(geom.skinInstance.bones,
                                                   geom.skinInstance.data.boneList):
                        if bonenode is lowest_bonenode:
                            lowest_geom = geom
                            lowest_bonedata = bonedata
                            break
                    else:
                        continue
                    break
                else:
                    raise RuntimeError("no reference geometry with this bone: bug?")
                # calculate matrix
                diff = (lowest_bonedata.getTransform()
                        * lowest_bonenode.getTransform(self)
                        * lowest_geom.getTransform(self).getInverse(fast=False))
                if diff.isIdentity():
                    logger.debug("%s is already in node position"
                                 % lowest_bonenode.name)
                    continue
                # now go over all geometries and synchronize their position to the
                # reference bone
                for geom in part:
                    logger.info("moving %s to node position" % geom.name)
                    # XXX we're using this trick a few times now
                    # XXX move it to a separate NiGeometry function
                    skininst = geom.skinInstance
                    skindata = skininst.data
                    # explanation:
                    # we must set the bonedata transform T' such that its bone bind
                    # position matrix
                    #   T'^-1 * G
                    # (where T' = the updated lowest_bonedata.getTransform()
                    # and G = geom.getTransform(self))
                    # coincides with the desired matrix
                    #   B = lowest_bonenode.getTransform(self)
                    # in other words:
                    #   T' = G * B^-1
                    # or, with diff = D = T * B * G^-1
                    #   T' = D^-1 * T
                    # to keep the geometry in sync, the vertices and normals must
                    # be multiplied with D, e.g. v' = v * D
                    # because the full transform
                    #    v * T * ... = v * D * D^-1 * T * ... = v' * T' * ...
                    # must be kept invariant
                    for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
                        logger.debug("transforming bind position of bone %s"
                                     % bonenode.name)
                        bonedata.setTransform(diff.getInverse(fast=False)
                                              * bonedata.getTransform())
                    # transform geometry
                    logger.debug("transforming vertices and normals")
                    for vert in geom.data.vertices:
                        newvert = vert * diff
                        vert.x = newvert.x
                        vert.y = newvert.y
                        vert.z = newvert.z
                    for norm in geom.data.normals:
                        newnorm = norm * diff.getMatrix33()
                        norm.x = newnorm.x
                        norm.y = newnorm.y
                        norm.z = newnorm.z

        def sendBonesToBindPosition(self):
            """This function will send all bones of geometries of this skeleton root
            to their bind position. For best results, call
            L{sendGeometriesToBindPosition} first.

            :return: A number quantifying the remaining difference between bind
                positions.
            :rtype: C{float}
            """
            # get logger
            logger = logging.getLogger("pyffi.nif.ninode")
            # check all bones and bone datas to see if a bind position exists
            bonelist = []
            error = 0.0
            geoms = list(self.getSkinnedGeometries())
            for geom in geoms:
                skininst = geom.skinInstance
                skindata = skininst.data
                for bonenode, bonedata in izip(skininst.bones, skindata.boneList):
                    # make sure all bone data of shared bones coincides
                    for othergeom, otherbonenode, otherbonedata in bonelist:
                        if bonenode is otherbonenode:
                            diff = ((otherbonedata.getTransform().getInverse(fast=False)
                                     *
                                     othergeom.getTransform(self))
                                    -
                                    (bonedata.getTransform().getInverse(fast=False)
                                     *
                                     geom.getTransform(self)))
                            if diff.supNorm() > 1e-3:
                                logger.warning("Geometries %s and %s do not share the same bind position: bone %s will be sent to a position matching only one of these" % (geom.name, othergeom.name, bonenode.name))
                            # break the loop
                            break
                    else:
                        # the loop did not break, so the bone was not yet added
                        # add it now
                        logger.debug("Found bind position data for %s" % bonenode.name)
                        bonelist.append((geom, bonenode, bonedata))

            # the algorithm simply makes all transforms correct by changing
            # each local bone matrix in such a way that the global matrix
            # relative to the skeleton root matches the skinning information

            # this algorithm is numerically most stable if bones are traversed
            # in hierarchical order, so first sort the bones
            sorted_bonelist = []
            for node in self.tree():
                if not isinstance(node, NifFormat.NiNode):
                    continue
                for geom, bonenode, bonedata in bonelist:
                    if node is bonenode:
                        sorted_bonelist.append((geom, bonenode, bonedata))
            bonelist = sorted_bonelist
            # now reposition the bones
            for geom, bonenode, bonedata in bonelist:
                # explanation:
                # v * CHILD * PARENT * ...
                # = v * CHILD * DIFF^-1 * DIFF * PARENT * ...
                # and now choose DIFF such that DIFF * PARENT * ... = desired transform

                # calculate desired transform relative to skeleton root
                # transform is DIFF * PARENT
                transform = (bonedata.getTransform().getInverse(fast=False)
                             * geom.getTransform(self))
                # calculate difference
                diff = transform * bonenode.getTransform(self).getInverse(fast=False)
                if not diff.isIdentity():
                    logger.info("Sending %s to bind position"
                                % bonenode.name)
                    # fix transform of this node
                    bonenode.setTransform(diff * bonenode.getTransform())
                    # fix transform of all its children
                    diff_inv = diff.getInverse(fast=False)
                    for childnode in bonenode.children:
                        if childnode:
                            childnode.setTransform(childnode.getTransform() * diff_inv)
                else:
                    logger.debug("%s is already in bind position"
                                 % bonenode.name)

            # validate
            error = 0.0
            diff_error = 0.0
            for geom in geoms:
                skininst = geom.skinInstance
                skindata = skininst.data
                # calculate geometry transform
                geomtransform = geom.getTransform(self)
                # check skin data fields (also see NiGeometry.updateBindPosition)
                for i, bone in enumerate(skininst.bones):
                    diff = ((skindata.boneList[i].getTransform().getInverse(fast=False)
                             * geomtransform)
                            - bone.getTransform(self))
                    # calculate error (sup norm)
                    diff_error = max(max(abs(elem) for elem in row)
                                     for row in diff.asList())
                    if diff_error > 1e-3:
                        logger.warning(
                            "Failed to set bind position of bone %s for geometry %s (error is %f)"
                            % (bone.name, geom.name, diff_error))
                    error = max(error, diff_error)

            logger.debug("Bone bind position maximal error is %f" % error)
            if error > 1e-3:
                logger.warning("Failed to send some bones to bind position")
            return error

    class NiObjectNET:
        def addExtraData(self, extrablock):
            """Add block to extra data list and extra data chain. It is good practice
            to ensure that the extra data has empty nextExtraData field when adding it
            to avoid loops in the hierarchy."""
            # add to the list
            num_extra = self.numExtraDataList
            self.numExtraDataList = num_extra + 1
            self.extraDataList.updateSize()
            self.extraDataList[num_extra] = extrablock
            # add to the chain
            if not self.extraData:
                self.extraData = extrablock
            else:
                lastextra = self.extraData
                while lastextra.nextExtraData:
                    lastextra = lastextra.nextExtraData
                lastextra.nextExtraData = extrablock

        def removeExtraData(self, extrablock):
            """Remove block from extra data list and extra data chain.

            >>> from PyFFI.Formats.NIF import NifFormat
            >>> block = NifFormat.NiNode()
            >>> block.numExtraDataList = 3
            >>> block.extraDataList.updateSize()
            >>> extrablock = NifFormat.NiStringExtraData()
            >>> block.extraDataList[1] = extrablock
            >>> block.removeExtraData(extrablock)
            >>> [extra for extra in block.extraDataList]
            [None, None]
            """
            # remove from list
            new_extra_list = []
            for extraother in self.extraDataList:
                if not extraother is extrablock:
                    new_extra_list.append(extraother)
            self.numExtraDataList = len(new_extra_list)
            self.extraDataList.updateSize()
            for i, extraother in enumerate(new_extra_list):
                self.extraDataList[i] = extraother
            # remove from chain
            if self.extraData is extrablock:
                self.extraData = extrablock.nextExtraData
            lastextra = self.extraData
            while lastextra:
                if lastextra.nextExtraData is extrablock:
                    lastextra.nextExtraData = lastextra.nextExtraData.nextExtraData
                lastextra = lastextra.nextExtraData

        def getExtraDatas(self):
            """Get a list of all extra data blocks."""
            xtras = [xtra for xtra in self.extraDataList]
            xtra = self.extraData
            while xtra:
                if not xtra in self.extraDataList:
                    xtras.append(xtra)
                xtra = xtra.nextExtraData
            return xtras

        def setExtraDatas(self, extralist):
            """Set all extra data blocks from given list (erases existing data).

            >>> from PyFFI.Formats.NIF import NifFormat
            >>> node = NifFormat.NiNode()
            >>> extra1 = NifFormat.NiExtraData()
            >>> extra1.name = "hello"
            >>> extra2 = NifFormat.NiExtraData()
            >>> extra2.name = "world"
            >>> node.getExtraDatas()
            []
            >>> node.setExtraDatas([extra1, extra2])
            >>> [extra.name for extra in node.getExtraDatas()]
            ['hello', 'world']
            >>> [extra.name for extra in node.extraDataList]
            ['hello', 'world']
            >>> node.extraData is extra1
            True
            >>> extra1.nextExtraData is extra2
            True
            >>> extra2.nextExtraData is None
            True
            >>> node.setExtraDatas([])
            >>> node.getExtraDatas()
            []
            >>> # now set them the other way around
            >>> node.setExtraDatas([extra2, extra1])
            >>> [extra.name for extra in node.getExtraDatas()]
            ['world', 'hello']
            >>> [extra.name for extra in node.extraDataList]
            ['world', 'hello']
            >>> node.extraData is extra2
            True
            >>> extra2.nextExtraData is extra1
            True
            >>> extra1.nextExtraData is None
            True

            :param extralist: List of extra data blocks to add.
            :type extralist: ``list`` of L{NifFormat.NiExtraData}
            """
            # set up extra data list
            self.numExtraDataList = len(extralist)
            self.extraDataList.updateSize()
            for i, extra in enumerate(extralist):
                self.extraDataList[i] = extra
            # set up extra data chain
            # first, kill the current chain
            self.extraData = None
            # now reconstruct it
            if extralist:
                self.extraData = extralist[0]
                lastextra = self.extraData
                for extra in extralist[1:]:
                    lastextra.nextExtraData = extra
                    lastextra = extra
                lastextra.nextExtraData = None

        def addController(self, ctrlblock):
            """Add block to controller chain and set target of controller to self."""
            if not self.controller:
                self.controller = ctrlblock
            else:
                lastctrl = self.controller
                while lastctrl.nextController:
                    lastctrl = lastctrl.nextController
                lastctrl.nextController = ctrlblock
            # set the target of the controller
            ctrlblock.target = self

        def getControllers(self):
            """Get a list of all controllers."""
            ctrls = []
            ctrl = self.controller
            while ctrl:
                ctrls.append(ctrl)
                ctrl = ctrl.nextController
            return ctrls

        def addIntegerExtraData(self, name, value):
            """Add a particular extra integer data block."""
            extra = NifFormat.NiIntegerExtraData()
            extra.name = name
            extra.integerData = value
            self.addExtraData(extra)

    class NiObject:
        def find(self, block_name = None, block_type = None):
            # does this block match the search criteria?
            if block_name and block_type:
                if isinstance(self, block_type):
                    try:
                        if block_name == self.name: return self
                    except AttributeError:
                        pass
            elif block_name:
                try:
                    if block_name == self.name: return self
                except AttributeError:
                    pass
            elif block_type:
                if isinstance(self, block_type): return self

            # ok, this block is not a match, so check further down in tree
            for child in self.getRefs():
                blk = child.find(block_name, block_type)
                if blk: return blk

            return None

        def findChain(self, block, block_type = None):
            """Finds a chain of blocks going from C{self} to C{block}. If found,
            self is the first element and block is the last element. If no branch
            found, returns an empty list. Does not check whether there is more
            than one branch; if so, the first one found is returned.

            :param block: The block to find a chain to.
            :param block_type: The type that blocks should have in this chain."""

            if self is block: return [self]
            for child in self.getRefs():
                if block_type and not isinstance(child, block_type): continue
                child_chain = child.findChain(block, block_type)
                if child_chain:
                    return [self] + child_chain

            return []

        def applyScale(self, scale):
            """Propagate scale down the hierarchy.
            Override this method if it contains geometry data that can be scaled.
            If overridden, call this base method to propagate scale down the hierarchy."""
            for child in self.getRefs():
                child.applyScale(scale)

        def tree(self, block_type = None, follow_all = True, unique = False):
            """A generator for parsing all blocks in the tree (starting from and
            including C{self}).

            :param block_type: If not ``None``, yield only blocks of the type C{block_type}.
            :param follow_all: If C{block_type} is not ``None``, then if this is ``True`` the function will parse the whole tree. Otherwise, the function will not follow branches that start by a non-C{block_type} block.

            :param unique: Whether the generator can return the same block twice or not."""
            # unique blocks: reduce this to the case of non-unique blocks
            if unique:
                block_list = []
                for block in self.tree(block_type = block_type, follow_all = follow_all, unique = False):
                    if not block in block_list:
                        yield block
                        block_list.append(block)
                return

            # yield self
            if not block_type:
                yield self
            elif isinstance(self, block_type):
                yield self
            elif not follow_all:
                return # don't recurse further

            # yield tree attached to each child
            for child in self.getRefs():
                for block in child.tree(block_type = block_type, follow_all = follow_all):
                    yield block

        def _validateTree(self):
            """Raises ValueError if there is a cycle in the tree."""
            # If the tree is parsed, then each block should be visited once.
            # However, as soon as some cycle is present, parsing the tree
            # will visit some child more than once (and as a consequence, infinitely
            # many times). So, walk the reference tree and check that every block is
            # only visited once.
            children = []
            for child in self.tree():
                if child in children:
                    raise ValueError('cyclic references detected')
                children.append(child)

        def isInterchangeable(self, other):
            """Are the two blocks interchangeable?

            @todo: Rely on AnyType, SimpleType, ComplexType, etc. implementation.
            """
            if isinstance(self, (NifFormat.NiProperty, NifFormat.NiSourceTexture)):
                # use hash for properties and source textures
                return ((self.__class__ is other.__class__)
                        and (self.getHash() == other.getHash()))
            else:
                # for blocks with references: quick check only
                return self is other

    class NiPixelData:
        def saveAsDDS(self, stream):
            """Save image as DDS file."""
            # set up header and pixel data
            data = PyFFI.Formats.DDS.DdsFormat.Data()
            header = data.header
            pixeldata = data.pixeldata

            # create header, depending on the format
            if self.pixelFormat in (NifFormat.PixelFormat.PX_FMT_RGB8,
                                    NifFormat.PixelFormat.PX_FMT_RGBA8):
                # uncompressed RGB(A)
                header.flags.caps = 1
                header.flags.height = 1
                header.flags.width = 1
                header.flags.pixelFormat = 1
                header.flags.mipmapCount = 1
                header.flags.linearSize = 1
                header.height = self.mipmaps[0].height
                header.width = self.mipmaps[0].width
                header.linearSize = len(self.pixelData)
                header.mipmapCount = len(self.mipmaps)
                header.pixelFormat.flags.rgb = 1
                header.pixelFormat.bitCount = self.bitsPerPixel
                header.pixelFormat.rMask = self.redMask
                header.pixelFormat.gMask = self.greenMask
                header.pixelFormat.bMask = self.blueMask
                header.pixelFormat.aMask = self.alphaMask
                header.caps1.complex = 1
                header.caps1.texture = 1
                header.caps1.mipmap = 1
                pixeldata.setValue(self.pixelData)
            elif self.pixelFormat == NifFormat.PixelFormat.PX_FMT_DXT1:
                # format used in Megami Tensei: Imagine
                header.flags.caps = 1
                header.flags.height = 1
                header.flags.width = 1
                header.flags.pixelFormat = 1
                header.flags.mipmapCount = 1
                header.flags.linearSize = 0
                header.height = self.mipmaps[0].height
                header.width = self.mipmaps[0].width
                header.linearSize = 0
                header.mipmapCount = len(self.mipmaps)
                header.pixelFormat.flags.fourcc = 1
                header.pixelFormat.fourcc = PyFFI.Formats.DDS.DdsFormat.FourCC.DXT1
                header.pixelFormat.bitCount = 0
                header.pixelFormat.rMask = 0
                header.pixelFormat.gMask = 0
                header.pixelFormat.bMask = 0
                header.pixelFormat.aMask = 0
                header.caps1.complex = 1
                header.caps1.texture = 1
                header.caps1.mipmap = 1
                pixeldata.setValue(''.join(self.pixelDataMatrix))
            elif self.pixelFormat in (NifFormat.PixelFormat.PX_FMT_DXT5,
                                      NifFormat.PixelFormat.PX_FMT_DXT5_ALT):
                # format used in Megami Tensei: Imagine
                header.flags.caps = 1
                header.flags.height = 1
                header.flags.width = 1
                header.flags.pixelFormat = 1
                header.flags.mipmapCount = 1
                header.flags.linearSize = 0
                header.height = self.mipmaps[0].height
                header.width = self.mipmaps[0].width
                header.linearSize = 0
                header.mipmapCount = len(self.mipmaps)
                header.pixelFormat.flags.fourcc = 1
                header.pixelFormat.fourcc = PyFFI.Formats.DDS.DdsFormat.FourCC.DXT5
                header.pixelFormat.bitCount = 0
                header.pixelFormat.rMask = 0
                header.pixelFormat.gMask = 0
                header.pixelFormat.bMask = 0
                header.pixelFormat.aMask = 0
                header.caps1.complex = 1
                header.caps1.texture = 1
                header.caps1.mipmap = 1
                pixeldata.setValue(''.join(self.pixelDataMatrix))
            else:
                raise ValueError(
                    "cannot save pixel format %i as DDS" % self.pixelFormat)

            data.write(stream)

    class NiSkinData:
        def getTransform(self):
            """Return scale, rotation, and translation into a single 4x4 matrix."""
            mat = NifFormat.Matrix44()
            mat.setScaleRotationTranslation(self.scale, self.rotation, self.translation)
            return mat

        def setTransform(self, mat):
            """Set rotation, transform, and velocity."""
            scale, rotation, translation = mat.getScaleRotationTranslation()

            self.scale = scale

            self.rotation.m11 = rotation.m11
            self.rotation.m12 = rotation.m12
            self.rotation.m13 = rotation.m13
            self.rotation.m21 = rotation.m21
            self.rotation.m22 = rotation.m22
            self.rotation.m23 = rotation.m23
            self.rotation.m31 = rotation.m31
            self.rotation.m32 = rotation.m32
            self.rotation.m33 = rotation.m33

            self.translation.x = translation.x
            self.translation.y = translation.y
            self.translation.z = translation.z

        def applyScale(self, scale):
            """Apply scale factor on data.

            >>> from PyFFI.Formats.NIF import NifFormat
            >>> id44 = NifFormat.Matrix44()
            >>> id44.setIdentity()
            >>> skelroot = NifFormat.NiNode()
            >>> skelroot.name = 'Scene Root'
            >>> skelroot.setTransform(id44)
            >>> bone1 = NifFormat.NiNode()
            >>> bone1.name = 'bone1'
            >>> bone1.setTransform(id44)
            >>> bone1.translation.x = 10
            >>> skelroot.addChild(bone1)
            >>> geom = NifFormat.NiTriShape()
            >>> geom.setTransform(id44)
            >>> skelroot.addChild(geom)
            >>> skininst = NifFormat.NiSkinInstance()
            >>> geom.skinInstance = skininst
            >>> skininst.skeletonRoot = skelroot
            >>> skindata = NifFormat.NiSkinData()
            >>> skininst.data = skindata
            >>> skindata.setTransform(id44)
            >>> geom.addBone(bone1, {})
            >>> geom.updateBindPosition()
            >>> bone1.translation.x
            10.0
            >>> skindata.boneList[0].translation.x
            -10.0
            >>> skelroot.applyScale(0.1)
            >>> bone1.translation.x
            1.0
            >>> skindata.boneList[0].translation.x
            -1.0
            """

            self.translation.x *= scale
            self.translation.y *= scale
            self.translation.z *= scale

            for skindata in self.boneList:
                skindata.translation.x *= scale
                skindata.translation.y *= scale
                skindata.translation.z *= scale
                skindata.boundingSphereOffset.x *= scale
                skindata.boundingSphereOffset.y *= scale
                skindata.boundingSphereOffset.z *= scale
                skindata.boundingSphereRadius *= scale

    class NiTransformInterpolator:
        def applyScale(self, scale):
            """Apply scale factor <scale> on data."""
            # apply scale on translation
            self.translation.x *= scale
            self.translation.y *= scale
            self.translation.z *= scale

            # apply scale on all blocks down the hierarchy
            NifFormat.NiObject.applyScale(self, scale)

    class NiTriBasedGeomData:
        def isInterchangeable(self, other):
            """Heuristically checks if two NiTriBasedGeomData blocks describe
            the same geometry, that is, if they can be used interchangeably in
            a nif file without affecting the rendering. The check is not fool
            proof but has shown to work in most practical cases.

            :param other: Another geometry data block.
            :type other: L{NifFormat.NiTriBasedGeomData} (if it has another type
                then the function will always return ``False``)
            :return: ``True`` if the geometries are equivalent, ``False`` otherwise.
            """
            # check for object identity
            if self is other:
                return True

            # type check
            if not isinstance(other, NifFormat.NiTriBasedGeomData):
                return False

            # check class
            if (not isinstance(self, other.__class__)
                or not isinstance(other, self.__class__)):
                return False

            # check some trivial things first
            for attribute in (
                "numVertices", "keepFlags", "compressFlags", "hasVertices",
                "numUvSets", "hasNormals", "center", "radius",
                "hasVertexColors", "hasUv", "consistencyFlags"):
                if getattr(self, attribute) != getattr(other, attribute):
                    return False

            # check vertices (this includes uvs, vcols and normals)
            verthashes1 = [hsh for hsh in self.getVertexHashGenerator()]
            verthashes2 = [hsh for hsh in other.getVertexHashGenerator()]
            for hash1 in verthashes1:
                if not hash1 in verthashes2:
                    return False
            for hash2 in verthashes2:
                if not hash2 in verthashes1:
                    return False

            # check triangle list
            triangles1 = [tuple(verthashes1[i] for i in tri)
                          for tri in self.getTriangles()]
            triangles2 = [tuple(verthashes2[i] for i in tri)
                          for tri in other.getTriangles()]
            for tri1 in triangles1:
                if not tri1 in triangles2:
                    return False
            for tri2 in triangles2:
                if not tri2 in triangles1:
                    return False

            # looks pretty identical!
            return True

        def getTriangleIndices(self, triangles):
            """Yield list of triangle indices (relative to
            self.getTriangles()) of given triangles. Degenerate triangles in
            the list are assigned index ``None``.

            >>> from PyFFI.Formats.NIF import NifFormat
            >>> geomdata = NifFormat.NiTriShapeData()
            >>> geomdata.setTriangles([(0,1,2),(1,2,3),(2,3,4)])
            >>> list(geomdata.getTriangleIndices([(1,2,3)]))
            [1]
            >>> list(geomdata.getTriangleIndices([(3,1,2)]))
            [1]
            >>> list(geomdata.getTriangleIndices([(2,3,1)]))
            [1]
            >>> list(geomdata.getTriangleIndices([(1,2,0),(4,2,3)]))
            [0, 2]
            >>> list(geomdata.getTriangleIndices([(0,0,0),(4,2,3)]))
            [None, 2]
            >>> list(geomdata.getTriangleIndices([(0,3,4),(4,2,3)])) # doctest: +ELLIPSIS
            Traceback (most recent call last):
                ...
            ValueError: ...

            :param triangles: An iterable of triangles to check.
            :type triangles: iterator or list of tuples of three ints
            """
            def triangleHash(triangle):
                """Calculate hash of a non-degenerate triangle.
                Returns ``None`` if the triangle is degenerate.
                """
                if triangle[0] < triangle[1] and triangle[0] < triangle[2]:
                    return hash((triangle[0], triangle[1], triangle[2]))
                elif triangle[1] < triangle[0] and triangle[1] < triangle[2]:
                    return hash((triangle[1], triangle[2], triangle[0]))
                elif triangle[2] < triangle[0] and triangle[2] < triangle[1]:
                    return hash((triangle[2], triangle[0], triangle[1]))

            # calculate hashes of all triangles in the geometry
            self_triangles_hashes = [
                triangleHash(triangle) for triangle in self.getTriangles()]

            # calculate index of each triangle in the list of triangles
            for triangle in triangles:
                triangle_hash = triangleHash(triangle)
                if triangle_hash is None:
                    yield None
                else:
                    yield self_triangles_hashes.index(triangle_hash)

    class NiTriBasedGeom:
        def getTangentSpace(self):
            """Return iterator over normal, tangent, bitangent vectors.
            If the block has no tangent space, then returns None.
            """

            def bytes2vectors(data, pos, num):
                for i in xrange(num):
                    # data[pos:pos+12] is not really well implemented, so do this
                    vecdata = ''.join(data[j] for j in xrange(pos, pos + 12))
                    vec = NifFormat.Vector3()
                    vec.x, vec.y, vec.z = struct.unpack('<fff', vecdata)
                    yield vec
                    pos += 12


            if self.data.numVertices == 0:
                return ()

            if not self.data.normals:
                #raise ValueError('geometry has no normals')
                return None

            if (not self.data.tangents) or (not self.data.bitangents):
                # no tangents and bitangents at the usual location
                # perhaps there is Oblivion style data?
                for extra in self.getExtraDatas():
                    if isinstance(extra, NifFormat.NiBinaryExtraData):
                        if extra.name == 'Tangent space (binormal & tangent vectors)':
                            break
                else:
                    #raise ValueError('geometry has no tangents')
                    return None
                if 24 * self.data.numVertices != len(extra.binaryData):
                    raise ValueError(
                        'tangent space data has invalid size, expected %i bytes but got %i'
                        % (24 * self.data.numVertices, len(extra.binaryData)))
                tangents = bytes2vectors(extra.binaryData,
                                         0,
                                         self.data.numVertices)
                bitangents = bytes2vectors(extra.binaryData,
                                           12 * self.data.numVertices,
                                           self.data.numVertices)
            else:
                tangents = self.data.tangents
                bitangents = self.data.bitangents

            return izip(self.data.normals, tangents, bitangents)

        def updateTangentSpace(self, as_extra=None):
            """Recalculate tangent space data.

            :param as_extra: Whether to store the tangent space data as extra data
                (as in Oblivion) or not (as in Fallout 3). If not set, switches to
                Oblivion if an extra data block is found, otherwise does default.
                Set it to override this detection (for example when using this
                function to create tangent space data) and force behaviour.
            """
            # check that self.data exists and is valid
            if not isinstance(self.data, NifFormat.NiTriBasedGeomData):
                raise ValueError(
                    'cannot update tangent space of a geometry with %s data'
                    %(self.data.__class__ if self.data else 'no'))

            verts = self.data.vertices
            norms = self.data.normals
            if len(self.data.uvSets) > 0:
                uvs   = self.data.uvSets[0]
            else:
                return # no uv sets so no tangent space

            # check that shape has norms and uvs
            if len(uvs) == 0 or len(norms) == 0: return

            bin = []
            tan = []
            for i in xrange(self.data.numVertices):
                bin.append(NifFormat.Vector3())
                tan.append(NifFormat.Vector3())

            # calculate tangents and binormals from vertex and texture coordinates
            for t1, t2, t3 in self.data.getTriangles():
                # skip degenerate triangles
                if t1 == t2 or t2 == t3 or t3 == t1: continue

                v1 = verts[t1]
                v2 = verts[t2]
                v3 = verts[t3]
                w1 = uvs[t1]
                w2 = uvs[t2]
                w3 = uvs[t3]
                v2v1 = v2 - v1
                v3v1 = v3 - v1
                w2w1 = w2 - w1
                w3w1 = w3 - w1

                # surface of triangle in texture space
                r = w2w1.u * w3w1.v - w3w1.u * w2w1.v

                # sign of surface
                r_sign = (1 if r >= 0 else -1)

                # contribution of this triangle to tangents and binormals
                sdir = NifFormat.Vector3()
                sdir.x = w3w1.v * v2v1.x - w2w1.v * v3v1.x
                sdir.y = w3w1.v * v2v1.y - w2w1.v * v3v1.y
                sdir.z = w3w1.v * v2v1.z - w2w1.v * v3v1.z
                sdir *= r_sign
                try:
                    sdir.normalize()
                except ZeroDivisionError: # catches zero vector
                    continue # skip triangle
                except ValueError: # catches invalid data
                    continue # skip triangle

                tdir = NifFormat.Vector3()
                tdir.x = w2w1.u * v3v1.x - w3w1.u * v2v1.x
                tdir.y = w2w1.u * v3v1.y - w3w1.u * v2v1.y
                tdir.z = w2w1.u * v3v1.z - w3w1.u * v2v1.z
                tdir *= r_sign
                try:
                    tdir.normalize()
                except ZeroDivisionError: # catches zero vector
                    continue # skip triangle
                except ValueError: # catches invalid data
                    continue # skip triangle

                # vector combination algorithm could possibly be improved
                for i in [t1, t2, t3]:
                    tan[i] += tdir
                    bin[i] += sdir

            xvec = NifFormat.Vector3()
            xvec.x = 1.0
            xvec.y = 0.0
            xvec.z = 0.0
            yvec = NifFormat.Vector3()
            yvec.x = 0.0
            yvec.y = 1.0
            yvec.z = 0.0
            for i in xrange(self.data.numVertices):
                n = norms[i]
                try:
                    n.normalize()
                except (ValueError, ZeroDivisionError):
                    # this happens if the normal has NAN values or is zero
                    # just pick something in that case
                    n = yvec
                try:
                    # turn n, bin, tan into a base via Gram-Schmidt
                    bin[i] -= n * (n * bin[i])
                    bin[i].normalize()
                    tan[i] -= n * (n * tan[i])
                    tan[i] -= bin[i] * (bin[i] * tan[i])
                    tan[i].normalize()
                except ZeroDivisionError:
                    # insuffient data to set tangent space for this vertex
                    # in that case pick a space
                    bin[i] = xvec.crossproduct(n)
                    try:
                        bin[i].normalize()
                    except ZeroDivisionError:
                        bin[i] = yvec.crossproduct(n)
                        bin[i].normalize() # should work now
                    tan[i] = n.crossproduct(bin[i])

            # find possible extra data block
            for extra in self.getExtraDatas():
                if isinstance(extra, NifFormat.NiBinaryExtraData):
                    if extra.name == 'Tangent space (binormal & tangent vectors)':
                        break
            else:
                extra = None

            # if autodetection is on, do as_extra only if an extra data block is found
            if as_extra is None:
                if extra:
                    as_extra = True
                else:
                    as_extra = False

            if as_extra:
                # if tangent space extra data already exists, use it
                if not extra:
                    # otherwise, create a new block and link it
                    extra = NifFormat.NiBinaryExtraData()
                    extra.name = 'Tangent space (binormal & tangent vectors)'
                    self.addExtraData(extra)

                # write the data
                binarydata = ""
                for vec in tan + bin:
                    binarydata += struct.pack('<fff', vec.x, vec.y, vec.z)
                extra.binaryData = binarydata
            else:
                # set tangent space flag
                self.data.numUvSets |= 61440
                self.data.bsNumUvSets |= 61440
                self.data.tangents.updateSize()
                self.data.bitangents.updateSize()
                for vec, data_tan in izip(tan, self.data.tangents):
                    data_tan.x = vec.x
                    data_tan.y = vec.y
                    data_tan.z = vec.z
                for vec, data_bitan in izip(bin, self.data.bitangents):
                    data_bitan.x = vec.x
                    data_bitan.y = vec.y
                    data_bitan.z = vec.z

        # ported from nifskope/skeleton.cpp:spSkinPartition
        def updateSkinPartition(self,
                                maxbonesperpartition=4, maxbonespervertex=4,
                                verbose=0, stripify=True, stitchstrips=False,
                                padbones=False,
                                triangles=None, trianglepartmap=None,
                                maximize_bone_sharing=False):
            """Recalculate skin partition data.

            :param maxbonesperpartition: Maximum number of bones in each partition.
                The numBones field will not exceed this number.
            :param maxbonespervertex: Maximum number of bones per vertex.
                The numWeightsPerVertex field will be exactly equal to this number.
            :param verbose: Ignored, and deprecated. Set pyffi's log level instead.
            :param stripify: If true, stripify the partitions, otherwise use triangles.
            :param stitchstrips: If stripify is true, then set this to true to stitch
                the strips.
            :param padbones: Enforces the numbones field to be equal to
                maxbonesperpartition. Also ensures that the bone indices are unique
                and sorted, per vertex. Raises an exception if maxbonespervertex
                is not equal to maxbonesperpartition (in that case bone indices cannot
                be unique and sorted). This options is required for Freedom Force vs.
                the 3rd Reich skin partitions.
            :param triangles: The triangles of the partition (if not specified, then
                this defaults to C{self.data.getTriangles()}.
            :param trianglepartmap: Maps each triangle to a partition index. Faces with
                different indices will never appear in the same partition. If the skin
                instance is a BSDismemberSkinInstance, then these indices are used as
                body part types, and the partitions in the BSDismemberSkinInstance are
                updated accordingly. Note that the faces are counted relative to
                L{triangles}.
            :param maximize_bone_sharing: Maximize bone sharing between partitions.
                This option is useful for Fallout 3.
            @deprecated: Do not use the verbose argument.
            """
            logger = logging.getLogger("pyffi.nif.nitribasedgeom")

            # if trianglepartmap not specified, map everything to index 0
            if trianglepartmap is None:
                trianglepartmap = repeat(0)

            # shortcuts relevant blocks
            if not self.skinInstance:
                # no skin, nothing to do
                return
            self._validateSkin()
            geomdata = self.data
            skininst = self.skinInstance
            skindata = skininst.data

            # get skindata vertex weights
            logger.debug("Getting vertex weights.")
            weights = self.getVertexWeights()

            # count minimum and maximum number of bones per vertex
            minbones = min(len(weight) for weight in weights)
            maxbones = max(len(weight) for weight in weights)
            if minbones <= 0:
                raise ValueError('bad NiSkinData: some vertices have no weights')
            logger.info("Counted minimum of %i and maximum of %i bones per vertex"
                        % (minbones, maxbones))

            # reduce bone influences to meet maximum number of bones per vertex
            logger.info("Imposing maximum of %i bones per vertex." % maxbonespervertex)
            lostweight = 0.0
            for weight in weights:
                if len(weight) > maxbonespervertex:
                    # delete bone influences with least weight
                    weight.sort(key=lambda x: x[1], reverse=True) # sort by weight
                    # save lost weight to return to user
                    lostweight = max(
                        lostweight, max(
                            [x[1] for x in weight[maxbonespervertex:]]))
                    del weight[maxbonespervertex:] # only keep first elements
                    # normalize
                    totalweight = sum([x[1] for x in weight]) # sum of all weights
                    for x in weight: x[1] /= totalweight
                    maxbones = maxbonespervertex
                # sort by again by bone (relied on later when matching vertices)
                weight.sort(key=lambda x: x[0])

            # reduce bone influences to meet maximum number of bones per partition
            # (i.e. maximum number of bones per triangle)
            logger.info(
                "Imposing maximum of %i bones per triangle (and hence, per partition)."
                % maxbonesperpartition)

            if triangles is None:
                triangles = geomdata.getTriangles()

            for tri in triangles:
                while True:
                    # find the bones influencing this triangle
                    tribones = []
                    for t in tri:
                        tribones.extend([bonenum for bonenum, boneweight in weights[t]])
                    tribones = set(tribones)
                    # target met?
                    if len(tribones) <= maxbonesperpartition:
                        break
                    # no, need to remove a bone

                    # sum weights for each bone to find the one that least influences
                    # this triangle
                    tribonesweights = {}
                    for bonenum in tribones: tribonesweights[bonenum] = 0.0
                    nono = set() # bones with weight 1 cannot be removed
                    for skinweights in [weights[t] for t in tri]:
                        # skinweights[0] is the first skinweight influencing vertex t
                        # and skinweights[0][0] is the bone number of that bone
                        if len(skinweights) == 1: nono.add(skinweights[0][0])
                        for bonenum, boneweight in skinweights:
                            tribonesweights[bonenum] += boneweight

                    # select a bone to remove
                    # first find bones we can remove

                    # restrict to bones not in the nono set
                    tribonesweights = [
                        x for x in tribonesweights.items() if x[0] not in nono]
                    if not tribonesweights:
                        raise ValueError(
                            "cannot remove anymore bones in this skin; "
                            "increase maxbonesperpartition and try again")
                    # sort by vertex weight sum the last element of this list is now a
                    # candidate for removal
                    tribonesweights.sort(key=lambda x: x[1], reverse=True)
                    minbone = tribonesweights[-1][0]

                    # remove minbone from all vertices of this triangle and from all
                    # matching vertices
                    for t in tri:
                        for tt in [t]: #match[t]:
                            # remove bone
                            weight = weights[tt]
                            for i, (bonenum, boneweight) in enumerate(weight):
                                if bonenum == minbone:
                                    # save lost weight to return to user
                                    lostweight = max(lostweight, boneweight)
                                    del weight[i]
                                    break
                            else:
                                continue
                            # normalize
                            totalweight = sum([x[1] for x in weight])
                            for x in weight:
                                x[1] /= totalweight

            # split triangles into partitions
            logger.info("Creating partitions")
            parts = []
            # keep creating partitions as long as there are triangles left
            while triangles:
                # create a partition
                part = [set(), [], None] # bones, triangles, partition index
                usedverts = set()
                addtriangles = True
                # keep adding triangles to it as long as the flag is set
                while addtriangles:
                    # newtriangles is a list of triangles that have not been added to
                    # the partition, similar for newtrianglepartmap
                    newtriangles = []
                    newtrianglepartmap = []
                    for tri, partindex in izip(triangles, trianglepartmap):
                        # find the bones influencing this triangle
                        tribones = []
                        for t in tri:
                            tribones.extend([
                                bonenum for bonenum, boneweight in weights[t]])
                        tribones = set(tribones)
                        # if part has no bones,
                        # or if part has all bones of tribones and index coincides
                        # then add this triangle to this part
                        if ((not part[0])
                            or ((part[0] >= tribones) and (part[2] == partindex))):
                            part[0] |= tribones
                            part[1].append(tri)
                            usedverts |= set(tri)
                            # if part was empty, assign it the index
                            if part[2] is None:
                                part[2] = partindex
                        else:
                            newtriangles.append(tri)
                            newtrianglepartmap.append(partindex)
                    triangles = newtriangles
                    trianglepartmap = newtrianglepartmap

                    # if we have room left in the partition
                    # then add adjacent triangles
                    addtriangles = False
                    newtriangles = []
                    newtrianglepartmap = []
                    if len(part[0]) < maxbonesperpartition:
                        for tri, partindex in izip(triangles, trianglepartmap):
                            # if triangle is adjacent, and has same index
                            # then check if it can be added to the partition
                            if (usedverts & set(tri)) and (part[2] == partindex):
                                # find the bones influencing this triangle
                                tribones = []
                                for t in tri:
                                    tribones.extend([
                                        bonenum for bonenum, boneweight in weights[t]])
                                tribones = set(tribones)
                                # and check if we exceed the maximum number of allowed
                                # bones
                                if len(part[0] | tribones) <= maxbonesperpartition:
                                    part[0] |= tribones
                                    part[1].append(tri)
                                    usedverts |= set(tri)
                                    # signal another try in adding triangles to
                                    # the partition
                                    addtriangles = True
                                else:
                                    newtriangles.append(tri)
                                    newtrianglepartmap.append(partindex)
                            else:
                                newtriangles.append(tri)
                                newtrianglepartmap.append(partindex)
                        triangles = newtriangles
                        trianglepartmap = newtrianglepartmap

                parts.append(part)

            logger.info("Created %i small partitions." % len(parts))

            # merge all partitions
            logger.info("Merging partitions.")
            merged = True # signals success, in which case do another run
            while merged:
                merged = False
                # newparts is to contain the updated merged partitions as we go
                newparts = []
                # addedparts is the set of all partitions from parts that have been
                # added to newparts
                addedparts = set()
                # try all combinations
                for a, parta in enumerate(parts):
                    if a in addedparts:
                        continue
                    newparts.append(parta)
                    addedparts.add(a)
                    for b, partb in enumerate(parts):
                        if b <= a:
                            continue
                        if b in addedparts:
                            continue
                        # if partition indices are the same, and bone limit is not
                        # exceeded, merge them
                        if ((parta[2] == partb[2])
                            and (len(parta[0] | partb[0]) <= maxbonesperpartition)):
                            parta[0] |= partb[0]
                            parta[1] += partb[1]
                            addedparts.add(b)
                            merged = True # signal another try in merging partitions
                # update partitions to the merged partitions
                parts = newparts

            # write the NiSkinPartition
            logger.info("Skin has %i partitions." % len(parts))

            # if skin partition already exists, use it
            if skindata.skinPartition != None:
                skinpart = skindata.skinPartition
                skininst.skinPartition = skinpart
            elif skininst.skinPartition != None:
                skinpart = skininst.skinPartition
                skindata.skinPartition = skinpart
            else:
            # otherwise, create a new block and link it
                skinpart = NifFormat.NiSkinPartition()
                skindata.skinPartition = skinpart
                skininst.skinPartition = skinpart

            # set number of partitions
            skinpart.numSkinPartitionBlocks = len(parts)
            skinpart.skinPartitionBlocks.updateSize()

            # maximize bone sharing, if requested
            if maximize_bone_sharing:
                logger.info("Maximizing shared bones.")
                # new list of partitions, sorted to maximize bone sharing
                newparts = []
                # as long as there are parts to add
                while parts:
                    # current set of partitions with shared bones
                    # starts a new set of partitions with shared bones
                    sharedparts = [parts.pop()]
                    sharedboneset = sharedparts[0][0]
                    # go over all other partitions, and try to add them with
                    # shared bones
                    oldparts = parts[:]
                    parts = []
                    for otherpart in oldparts:
                        # check if bones can be added
                        if len(sharedboneset | otherpart[0]) <= maxbonesperpartition:
                            # ok, we can share bones!
                            # update set of shared bones
                            sharedboneset |= otherpart[0]
                            # add this other partition to list of shared parts
                            sharedparts.append(otherpart)
                            # update bone set in all shared parts
                            for sharedpart in sharedparts:
                                sharedpart[0] = sharedboneset
                        else:
                            # not added to sharedparts,
                            # so we must keep it for the next iteration
                            parts.append(otherpart)
                    # update list of partitions
                    newparts.extend(sharedparts)

                # store update
                parts = newparts

            # for Fallout 3, set dismember partition indices
            if isinstance(skininst, NifFormat.BSDismemberSkinInstance):
                skininst.numPartitions = len(parts)
                skininst.partitions.updateSize()
                lastpart = None
                for bodypart, part in izip(skininst.partitions, parts):
                    bodypart.bodyPart = part[2]
                    if (lastpart is None) or (lastpart[0] != part[0]):
                        # start new bone set, if bones are not shared
                        bodypart.partFlag.startNewBoneset = 1
                    else:
                        # do not start new bone set
                        bodypart.partFlag.startNewBoneset = 0
                    # caps are invisible
                    bodypart.partFlag.editorVisible = (part[2] < 100
                                                       or part[2] >= 1000)
                    # store part for next iteration
                    lastpart = part

            for skinpartblock, part in zip(skinpart.skinPartitionBlocks, parts):
                # get sorted list of bones
                bones = sorted(list(part[0]))
                triangles = part[1]
                # get sorted list of vertices
                vertices = set()
                for tri in triangles:
                    vertices |= set(tri)
                vertices = sorted(list(vertices))
                # remap the vertices
                parttriangles = []
                for tri in triangles:
                    parttriangles.append([vertices.index(t) for t in tri])
                if stripify:
                    # stripify the triangles
                    logger.info("Stripifying partition %i" % parts.index(part))
                    strips = PyFFI.Utils.TriStrip.stripify(
                        parttriangles, stitchstrips=stitchstrips)
                    numtriangles = 0
                    for strip in strips:
                        numtriangles += len(strip) - 2
                else:
                    numtriangles = len(parttriangles)

                # set all the data
                skinpartblock.numVertices = len(vertices)
                skinpartblock.numTriangles = numtriangles
                if not padbones:
                    skinpartblock.numBones = len(bones)
                else:
                    if maxbonesperpartition != maxbonespervertex:
                        raise ValueError(
                            "when padding bones maxbonesperpartition must be "
                            "equal to maxbonespervertex")
                    # freedom force vs. the 3rd reich needs exactly 4 bones per
                    # partition on every partition block
                    skinpartblock.numBones = maxbonesperpartition
                if stripify:
                    skinpartblock.numStrips = len(strips)
                else:
                    skinpartblock.numStrips = 0
                # maxbones would be enough as numWeightsPerVertex but the Gamebryo
                # engine doesn't like that, it seems to want exactly 4 even if there
                # are fewer
                skinpartblock.numWeightsPerVertex = maxbonespervertex
                skinpartblock.bones.updateSize()
                for i, bonenum in enumerate(bones):
                    skinpartblock.bones[i] = bonenum
                for i in xrange(len(bones), skinpartblock.numBones):
                    skinpartblock.bones[i] = 0 # dummy bone slots refer to first bone
                skinpartblock.hasVertexMap = True
                skinpartblock.vertexMap.updateSize()
                for i, v in enumerate(vertices):
                    skinpartblock.vertexMap[i] = v
                skinpartblock.hasVertexWeights = True
                skinpartblock.vertexWeights.updateSize()
                for i, v in enumerate(vertices):
                    for j in xrange(skinpartblock.numWeightsPerVertex):
                        if j < len(weights[v]):
                            skinpartblock.vertexWeights[i][j] = weights[v][j][1]
                        else:
                            skinpartblock.vertexWeights[i][j] = 0.0
                if stripify:
                    skinpartblock.hasFaces = True
                    skinpartblock.stripLengths.updateSize()
                    for i, strip in enumerate(strips):
                        skinpartblock.stripLengths[i] = len(strip)
                    skinpartblock.strips.updateSize()
                    for i, strip in enumerate(strips):
                        for j, v in enumerate(strip):
                            skinpartblock.strips[i][j] = v
                else:
                    skinpartblock.hasFaces = True
                    # clear strip lengths array
                    skinpartblock.stripLengths.updateSize()
                    # clear strips array
                    skinpartblock.strips.updateSize()
                    skinpartblock.triangles.updateSize()
                    for i, (v1,v2,v3) in enumerate(parttriangles):
                        skinpartblock.triangles[i].v1 = v1
                        skinpartblock.triangles[i].v2 = v2
                        skinpartblock.triangles[i].v3 = v3
                skinpartblock.hasBoneIndices = True
                skinpartblock.boneIndices.updateSize()
                for i, v in enumerate(vertices):
                    # the boneindices set keeps track of indices that have not been
                    # used yet
                    boneindices = set(range(skinpartblock.numBones))
                    for j in xrange(len(weights[v])):
                        skinpartblock.boneIndices[i][j] = bones.index(weights[v][j][0])
                        boneindices.remove(skinpartblock.boneIndices[i][j])
                    for j in xrange(len(weights[v]),skinpartblock.numWeightsPerVertex):
                        if padbones:
                            # if padbones is True then we have enforced
                            # numBones == numWeightsPerVertex so this will not trigger
                            # a KeyError
                            skinpartblock.boneIndices[i][j] = boneindices.pop()
                        else:
                            skinpartblock.boneIndices[i][j] = 0

                # sort weights
                for i, v in enumerate(vertices):
                    vweights = []
                    for j in xrange(skinpartblock.numWeightsPerVertex):
                        vweights.append([
                            skinpartblock.boneIndices[i][j],
                            skinpartblock.vertexWeights[i][j]])
                    if padbones:
                        # by bone index (for ffvt3r)
                        vweights.sort(key=lambda w: w[0])
                    else:
                        # by weight (for fallout 3, largest weight first)
                        vweights.sort(key=lambda w: -w[1])
                    for j in xrange(skinpartblock.numWeightsPerVertex):
                        skinpartblock.boneIndices[i][j] = vweights[j][0]
                        skinpartblock.vertexWeights[i][j] = vweights[j][1]

            return lostweight

        # ported from nifskope/skeleton.cpp:spFixBoneBounds
        def updateSkinCenterRadius(self):
            """Update centers and radii of all skin data fields."""
            # shortcuts relevant blocks
            if not self.skinInstance:
                return # no skin, nothing to do
            self._validateSkin()
            geomdata = self.data
            skininst = self.skinInstance
            skindata = skininst.data

            verts = geomdata.vertices

            for skindatablock in skindata.boneList:
                # find all vertices influenced by this bone
                boneverts = [verts[skinweight.index]
                             for skinweight in skindatablock.vertexWeights]

                # find bounding box of these vertices
                low = NifFormat.Vector3()
                low.x = min(v.x for v in boneverts)
                low.y = min(v.y for v in boneverts)
                low.z = min(v.z for v in boneverts)

                high = NifFormat.Vector3()
                high.x = max(v.x for v in boneverts)
                high.y = max(v.y for v in boneverts)
                high.z = max(v.z for v in boneverts)

                # center is in the center of the bounding box
                center = (low + high) * 0.5

                # radius is the largest distance from the center
                r2 = 0.0
                for v in boneverts:
                    d = center - v
                    r2 = max(r2, d.x*d.x+d.y*d.y+d.z*d.z)
                radius = r2 ** 0.5

                # transform center in proper coordinates (radius remains unaffected)
                center *= skindatablock.getTransform()

                # save data
                skindatablock.boundingSphereOffset.x = center.x
                skindatablock.boundingSphereOffset.y = center.y
                skindatablock.boundingSphereOffset.z = center.z
                skindatablock.boundingSphereRadius = radius

        def getInterchangeableTriShape(self):
            """Returns a NiTriShape block that is geometrically interchangeable."""
            # copy the shape (first to NiTriBasedGeom and then to NiTriShape)
            shape = NifFormat.NiTriShape().deepcopy(
                NifFormat.NiTriBasedGeom().deepcopy(self))
            # copy the geometry without strips
            shapedata = NifFormat.NiTriShapeData().deepcopy(
                NifFormat.NiTriBasedGeomData().deepcopy(self.data))
            # update the shape data
            shapedata.setTriangles(self.data.getTriangles())
            # relink the shape data
            shape.data = shapedata
            # and return the result
            return shape

        def getInterchangeableTriStrips(self):
            """Returns a NiTriStrips block that is geometrically interchangeable."""
            # copy the shape (first to NiTriBasedGeom and then to NiTriStrips)
            strips = NifFormat.NiTriStrips().deepcopy(
                NifFormat.NiTriBasedGeom().deepcopy(self))
            # copy the geometry without triangles
            stripsdata = NifFormat.NiTriStripsData().deepcopy(
                NifFormat.NiTriBasedGeomData().deepcopy(self.data))
            # update the shape data
            stripsdata.setTriangles(self.data.getTriangles())
            # relink the shape data
            strips.data = stripsdata
            # and return the result
            return strips

    class NiTriShapeData:
        """
        Example usage:

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> block = NifFormat.NiTriShapeData()
        >>> block.setTriangles([(0,1,2),(2,1,3),(2,3,4)])
        >>> block.getStrips()
        [[4, 4, 3, 2, 1, 0]]
        >>> block.getTriangles()
        [(0, 1, 2), (2, 1, 3), (2, 3, 4)]
        >>> block.setStrips([[1,0,1,2,3,4]])
        >>> block.getStrips()
        [[0, 0, 1, 2, 3, 4]]
        >>> block.getTriangles()
        [(0, 2, 1), (1, 2, 3), (2, 4, 3)]
        """
        def getTriangles(self):
            return [(t.v1, t.v2, t.v3) for t in self.triangles]

        def setTriangles(self, triangles, stitchstrips = False):
            # note: the stitchstrips argument is ignored - only present to ensure
            # uniform interface between NiTriShapeData and NiTriStripsData

            # initialize triangle array
            n = len(triangles)
            self.numTriangles = n
            self.numTrianglePoints = 3*n
            self.hasTriangles = (n > 0)
            self.triangles.updateSize()

            # copy triangles
            src = triangles.__iter__()
            dst = self.triangles.__iter__()
            for k in xrange(n):
                dst_t = dst.next()
                dst_t.v1, dst_t.v2, dst_t.v3 = src.next()

        def getStrips(self):
            return PyFFI.Utils.TriStrip.stripify(self.getTriangles())

        def setStrips(self, strips):
            self.setTriangles(PyFFI.Utils.TriStrip.triangulate(strips))

    class NiTriStripsData:
        """
        Example usage:

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> block = NifFormat.NiTriStripsData()
        >>> block.setTriangles([(0,1,2),(2,1,3),(2,3,4)])
        >>> block.getStrips()
        [[4, 4, 3, 2, 1, 0]]
        >>> block.getTriangles()
        [(4, 2, 3), (3, 2, 1), (2, 0, 1)]
        >>> block.setStrips([[1,0,1,2,3,4]])
        >>> block.getStrips()
        [[1, 0, 1, 2, 3, 4]]
        >>> block.getTriangles()
        [(0, 2, 1), (1, 2, 3), (2, 4, 3)]
        """
        def getTriangles(self):
            return PyFFI.Utils.TriStrip.triangulate(self.points)

        def setTriangles(self, triangles, stitchstrips = False):
            self.setStrips(PyFFI.Utils.TriStrip.stripify(triangles, stitchstrips = stitchstrips))

        def getStrips(self):
            return [[i for i in strip] for strip in self.points]

        def setStrips(self, strips):
            # initialize strips array
            self.numStrips = len(strips)
            self.stripLengths.updateSize()
            numtriangles = 0
            for i, strip in enumerate(strips):
                self.stripLengths[i] = len(strip)
                numtriangles += len(strip) - 2
            self.numTriangles = numtriangles
            self.points.updateSize()
            self.hasPoints = (len(strips) > 0)

            # copy strips
            for i, strip in enumerate(strips):
                for j, idx in enumerate(strip):
                    self.points[i][j] = idx

    class RagdollDescriptor:
        def updateAB(self, transform):
            """Update B pivot and axes from A using the given transform."""
            # pivot point
            pivotB = ((7 * self.pivotA.getVector3()) * transform) / 7.0
            self.pivotB.x = pivotB.x
            self.pivotB.y = pivotB.y
            self.pivotB.z = pivotB.z
            # axes (rotation only)
            transform = transform.getMatrix33()
            planeB = self.planeA.getVector3() *  transform
            twistB = self.twistA.getVector3() *  transform
            self.planeB.x = planeB.x
            self.planeB.y = planeB.y
            self.planeB.z = planeB.z
            self.twistB.x = twistB.x
            self.twistB.y = twistB.y
            self.twistB.z = twistB.z

    class SkinData:
        def getTransform(self):
            """Return scale, rotation, and translation into a single 4x4 matrix."""
            m = NifFormat.Matrix44()
            m.setScaleRotationTranslation(self.scale, self.rotation, self.translation)
            return m

        def setTransform(self, m):
            """Set rotation, transform, and velocity."""
            scale, rotation, translation = m.getScaleRotationTranslation()

            self.scale = scale

            self.rotation.m11 = rotation.m11
            self.rotation.m12 = rotation.m12
            self.rotation.m13 = rotation.m13
            self.rotation.m21 = rotation.m21
            self.rotation.m22 = rotation.m22
            self.rotation.m23 = rotation.m23
            self.rotation.m31 = rotation.m31
            self.rotation.m32 = rotation.m32
            self.rotation.m33 = rotation.m33

            self.translation.x = translation.x
            self.translation.y = translation.y
            self.translation.z = translation.z

    class StringPalette:
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

    class TexCoord:
        def asList(self):
            return [self.u, self.v]

        def normalize(self):
            r = (self.u*self.u + self.v*self.v) ** 0.5
            if r < NifFormat._EPSILON:
                raise ZeroDivisionError('cannot normalize vector %s'%self)
            self.u /= r
            self.v /= r

        def __str__(self):
            return "[ %6.3f %6.3f ]"%(self.u, self.v)

        def __mul__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.TexCoord()
                v.u = self.u * x
                v.v = self.v * x
                return v
            elif isinstance(x, NifFormat.TexCoord):
                return self.u * x.u + self.v * x.v
            else:
                raise TypeError("do not know how to multiply TexCoord with %s"%x.__class__)

        def __rmul__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.TexCoord()
                v.u = x * self.u
                v.v = x * self.v
                return v
            else:
                raise TypeError("do not know how to multiply %s and TexCoord"%x.__class__)

        def __add__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.TexCoord()
                v.u = self.u + x
                v.v = self.v + x
                return v
            elif isinstance(x, NifFormat.TexCoord):
                v = NifFormat.TexCoord()
                v.u = self.u + x.u
                v.v = self.v + x.v
                return v
            else:
                raise TypeError("do not know how to add TexCoord and %s"%x.__class__)

        def __radd__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.TexCoord()
                v.u = x + self.u
                v.v = x + self.v
                return v
            else:
                raise TypeError("do not know how to add %s and TexCoord"%x.__class__)

        def __sub__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.TexCoord()
                v.u = self.u - x
                v.v = self.v - x
                return v
            elif isinstance(x, NifFormat.TexCoord):
                v = NifFormat.TexCoord()
                v.u = self.u - x.u
                v.v = self.v - x.v
                return v
            else:
                raise TypeError("do not know how to substract TexCoord and %s"%x.__class__)

        def __rsub__(self, x):
            if isinstance(x, (float, int, long)):
                v = NifFormat.TexCoord()
                v.u = x - self.u
                v.v = x - self.v
                return v
            else:
                raise TypeError("do not know how to substract %s and TexCoord"%x.__class__)

        def __neg__(self):
            v = NifFormat.TexCoord()
            v.u = -self.u
            v.v = -self.v
            return v
