"""
:mod:`PyFFI.Formats.CGF` --- Crytek (.cgf and .cga)
===================================================

Regression tests
----------------

Read a CGF file
^^^^^^^^^^^^^^^

>>> # get file version and file type, and read cgf file
>>> stream = open('tests/cgf/test.cgf', 'rb')
>>> data = CgfFormat.Data()
>>> # read chunk table only
>>> data.inspect(stream)
>>> # check chunk types
>>> list(chunktype.__name__ for chunktype in data.chunk_table.getChunkTypes())
['SourceInfoChunk', 'TimingChunk']
>>> data.chunks # no chunks yet
[]
>>> # read full file
>>> data.read(stream)
>>> # get all chunks
>>> for chunk in data.chunks:
...     print(chunk) # doctest: +ELLIPSIS
<class 'PyFFI.Formats.CGF.SourceInfoChunk'> instance at ...
* sourceFile : <EMPTY STRING>
* date : Fri Sep 28 22:40:44 2007
* author : blender@BLENDER
<BLANKLINE>
<class 'PyFFI.Formats.CGF.TimingChunk'> instance at ...
* secsPerTick : 0.000208333338378
* ticksPerFrame : 160
* globalRange :
    <class 'PyFFI.Formats.CGF.RangeEntity'> instance at ...
    * name : GlobalRange
    * start : 0
    * end : 100
* numSubRanges : 0
<BLANKLINE>

Parse all CGF files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in CgfFormat.walkData('tests/cgf'):
...     print(stream.name)
...     try:
...         data.read(stream)
...     except StandardError:
...         print("Warning: read failed due corrupt file, corrupt format description, or bug.")
...     print(len(data.chunks))
...     # do something with the chunks
...     for chunk in data.chunks:
...         chunk.applyScale(2.0)
tests/cgf/invalid.cgf
Warning: read failed due corrupt file, corrupt format description, or bug.
0
tests/cgf/monkey.cgf
14
tests/cgf/test.cgf
2
tests/cgf/vcols.cgf
6

Create a CGF file from scratch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> from PyFFI.Formats.CGF import CgfFormat
>>> node1 = CgfFormat.NodeChunk()
>>> node1.name = "hello"
>>> node2 = CgfFormat.NodeChunk()
>>> node1.numChildren = 1
>>> node1.children.updateSize()
>>> node1.children[0] = node2
>>> node2.name = "world"
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> data = CgfFormat.Data() # default is far cry
>>> data.chunks = [node1, node2]
>>> # note: write returns number of padding bytes
>>> data.write(stream)
0
>>> stream.seek(0)
>>> data.inspectVersionOnly(stream)
>>> hex(data.header.version)
'0x744'
>>> data.read(stream)
>>> # get all chunks
>>> for chunk in data.chunks:
...     print(chunk) # doctest: +ELLIPSIS +REPORT_NDIFF
<class 'PyFFI.Formats.CGF.NodeChunk'> instance at 0x...
* name : hello
* object : None
* parent : None
* numChildren : 1
* material : None
* isGroupHead : False
* isGroupMember : False
* reserved1 :
    <class 'PyFFI.object_models.xml.Array.Array'> instance at 0x...
    0: 0
    1: 0
* transform :
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
* pos : [  0.000  0.000  0.000 ]
* rot :
    <class 'PyFFI.Formats.CGF.Quat'> instance at 0x...
    * x : 0.0
    * y : 0.0
    * z : 0.0
    * w : 0.0
* scl : [  0.000  0.000  0.000 ]
* posCtrl : None
* rotCtrl : None
* sclCtrl : None
* propertyString : <EMPTY STRING>
* children :
    <class 'PyFFI.object_models.xml.Array.Array'> instance at 0x...
    0: <class 'PyFFI.Formats.CGF.NodeChunk'> instance at 0x...
<BLANKLINE>
<class 'PyFFI.Formats.CGF.NodeChunk'> instance at 0x...
* name : world
* object : None
* parent : None
* numChildren : 0
* material : None
* isGroupHead : False
* isGroupMember : False
* reserved1 :
    <class 'PyFFI.object_models.xml.Array.Array'> instance at 0x...
    0: 0
    1: 0
* transform :
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
* pos : [  0.000  0.000  0.000 ]
* rot :
    <class 'PyFFI.Formats.CGF.Quat'> instance at 0x...
    * x : 0.0
    * y : 0.0
    * z : 0.0
    * w : 0.0
* scl : [  0.000  0.000  0.000 ]
* posCtrl : None
* rotCtrl : None
* sclCtrl : None
* propertyString : <EMPTY STRING>
* children : <class 'PyFFI.object_models.xml.Array.Array'> instance at 0x...
<BLANKLINE>
"""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
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

import itertools
import logging
import struct
import os
import re
import warnings
from itertools import izip


import PyFFI.object_models.Common
import PyFFI.object_models
import PyFFI.object_models.xml
import PyFFI.utils.math
import PyFFI.utils.tangentspace
from PyFFI.object_models.xml.Basic import BasicBase
from PyFFI.utils.graph import EdgeFilter

class _MetaCgfFormat(PyFFI.object_models.xml.FileFormat.__metaclass__):
    """Metaclass which constructs the chunk map during class creation."""
    def __init__(cls, name, bases, dct):
        super(_MetaCgfFormat, cls).__init__(name, bases, dct)
        
        # map chunk type integers to chunk type classes
        cls.CHUNK_MAP = dict(
            (getattr(cls.ChunkType, chunk_name),
             getattr(cls, '%sChunk' % chunk_name))
            for chunk_name in cls.ChunkType._enumkeys
            if chunk_name != "ANY")

class CgfFormat(PyFFI.object_models.xml.FileFormat):
    """Stores all information about the cgf file format."""
    __metaclass__ = _MetaCgfFormat
    xmlFileName = 'cgf.xml'
    # where to look for cgf.xml and in what order: CGFXMLPATH env var,
    # or module directory
    xmlFilePath = [os.getenv('CGFXMLPATH'), os.path.dirname(__file__)]
    EPSILON = 0.0001 # used for comparing floats
    # regular expression for file name extension matching on cgf files
    RE_FILENAME = re.compile(r'^.*\.(cgf|cga|chr|caf)$', re.IGNORECASE)

    # version and user version for far cry
    VER_FARCRY = 0x744
    UVER_FARCRY = 1

    # version and user version for crysis
    VER_CRYSIS = 0x744
    UVER_CRYSIS = 2

    # basic types
    int = PyFFI.object_models.Common.Int
    uint = PyFFI.object_models.Common.UInt
    byte = PyFFI.object_models.Common.Byte
    ubyte = PyFFI.object_models.Common.UByte
    short = PyFFI.object_models.Common.Short
    ushort = PyFFI.object_models.Common.UShort
    char = PyFFI.object_models.Common.Char
    float = PyFFI.object_models.Common.Float
    bool = PyFFI.object_models.Common.Bool
    String = PyFFI.object_models.Common.ZString
    SizedString = PyFFI.object_models.Common.SizedString

     # implementation of cgf-specific basic types

    class String16(PyFFI.object_models.Common.FixedString):
        """String of fixed length 16."""
        _len = 16

    class String32(PyFFI.object_models.Common.FixedString):
        """String of fixed length 32."""
        _len = 32

    class String64(PyFFI.object_models.Common.FixedString):
        """String of fixed length 64."""
        _len = 64

    class String128(PyFFI.object_models.Common.FixedString):
        """String of fixed length 128."""
        _len = 128

    class String256(PyFFI.object_models.Common.FixedString):
        """String of fixed length 256."""
        _len = 256

    class FileSignature(BasicBase):
        """The CryTek file signature with which every
        cgf file starts."""
        def __init__(self, **kwargs):
            super(CgfFormat.FileSignature, self).__init__(**kwargs)

        def __str__(self):
            return 'CryTek\x00\x00'

        def read(self, stream, **kwargs):
            """Read signature from stream.

            :param stream: The stream to read from.
            :type stream: file
            """
            signat = stream.read(8)
            if signat[:6] != self.__str__()[:6].encode("ascii"):
                raise ValueError(
                    "invalid CGF signature: expected '%s' but got '%s'"
                    %(self.__str__(), signat))

        def write(self, stream, **kwargs):
            """Write signature to stream.

            :param stream: The stream to read from.
            :type stream: file
            """
            stream.write(self.__str__().encode("ascii"))

        def getValue(self):
            """Get signature.

            :return: The signature.
            """
            return self.__str__()

        def setValue(self, value):
            """Set signature.

            :param value: The value to assign (should be 'Crytek\\x00\\x00').
            :type value: str
            """
            if value != self.__str__():
                raise ValueError(
                    "invalid CGF signature: expected '%s' but got '%s'"
                    %(self.__str__(), value))

        def getSize(self, **kwargs):
            """Return number of bytes that the signature occupies in a file.

            :return: Number of bytes.
            """
            return 8

        def getHash(self, **kwargs):
            """Return a hash value for the signature.

            :return: An immutable object that can be used as a hash.
            """
            return self.__str__()

    class Ref(BasicBase):
        """Reference to a chunk, up the hierarchy."""
        _isTemplate = True
        _hasLinks = True
        _hasRefs = True
        def __init__(self, **kwargs):
            super(CgfFormat.Ref, self).__init__(**kwargs)
            self._template = kwargs.get('template', type(None))
            self._value = None

        def getValue(self):
            """Get chunk being referred to.

            :return: The chunk being referred to.
            """
            return self._value

        def setValue(self, value):
            """Set chunk reference.

            :param value: The value to assign.
            :type value: L{CgfFormat.Chunk}
            """
            if value == None:
                self._value = None
            else:
                if not isinstance(value, self._template):
                    raise TypeError(
                        'expected an instance of %s but got instance of %s'
                        %(self._template, value.__class__))
                self._value = value

        def read(self, stream, **kwargs):
            """Read chunk index.

            :param stream: The stream to read from.
            :type stream: file
            :keyword link_stack: The stack containing all block indices.
            :type link_stack: list of ints
            """
            self._value = None # fixLinks will set this field
            block_index, = struct.unpack('<i', stream.read(4))
            kwargs.get('link_stack', []).append(block_index)

        def write(self, stream, **kwargs):
            """Write chunk index.

            :param stream: The stream to write to.
            :type stream: file
            :keyword block_index_dct: Dictionary mapping blocks to indices.
            :type block_index_dct: dict
            """
            if self._value == None:
                stream.write('\xff\xff\xff\xff')
            else:
                stream.write(struct.pack(
                    '<i', kwargs.get('block_index_dct')[self._value]))

        def fixLinks(self, **kwargs):
            """Resolve chunk index into a chunk.

            :keyword block_dct: Dictionary mapping block index to block.
            :type block_dct: dict
            :keyword link_stack: The stack containing all block indices.
            :type link_stack: list of ints
            """
            logger = logging.getLogger("pyffi.cgf.data")
            block_index = kwargs.get('link_stack').pop(0)
            # case when there's no link
            if block_index == -1:
                self._value = None
                return
            # other case: look up the link and check the link type
            try:
                block = kwargs.get('block_dct')[block_index]
            except KeyError:
                # make this raise an exception when all reference errors
                # are sorted out
                logger.warn("invalid chunk reference (%i)" % block_index)
                self._value = None
                return
            if not isinstance(block, self._template):
                if block_index == 0:
                    # crysis often uses index 0 to refer to an invalid index
                    # so don't complain on this one
                    block = None
                else:
                    # make this raise an exception when all reference errors
                    # are sorted out
                    logger.warn("""\
expected instance of %s
but got instance of %s""" % (self._template, block.__class__))
            self._value = block

        def getLinks(self, **kwargs):
            """Return the chunk reference.

            :return: Empty list if no reference, or single item list containing
                the reference.
            """
            if self._value != None:
                return [self._value]
            else:
                return []

        def getRefs(self, **kwargs):
            """Return the chunk reference.

            :return: Empty list if no reference, or single item list containing
                the reference.
            """
            if self._value != None:
                return [self._value]
            else:
                return []

        def __str__(self):
            # don't recurse
            if self._value != None:
                return '%s instance at 0x%08X'\
                       % (self._value.__class__, id(self._value))
            else:
                return 'None'

        def getSize(self, **kwargs):
            """Return number of bytes this type occupies in a file.

            :return: Number of bytes.
            """
            return 4

        def getHash(self, **kwargs):
            """Return a hash value for the chunk referred to.

            :return: An immutable object that can be used as a hash.
            """
            return self._value.getHash() if not self._value is None else None

    class Ptr(Ref):
        """Reference to a chunk, down the hierarchy."""
        _isTemplate = True
        _hasLinks = True
        _hasRefs = False

        def __str__(self):
            # avoid infinite recursion
            if self._value != None:
                return '%s instance at 0x%08X'\
                       % (self._value.__class__, id(self._value))
            else:
                return 'None'

        def getRefs(self, **kwargs):
            """Ptr does not point down, so getRefs returns empty list.

            :return: C{[]}
            """
            return []

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        :param version_str: The version string.
        :type version_str: str
        :return: A version integer.

        >>> hex(CgfFormat.versionNumber('744'))
        '0x744'
        """
        return int(version_str, 16)

    # exceptions
    class CgfError(StandardError):
        """Exception for CGF specific errors."""
        pass

    @classmethod
    def getVersion(cls, stream):
        """Returns version of the chunk table, and game as user_version.
        Far Cry is user_version L{CgfFormat.UVER_FARCRY} and Crysis is
        user_version L{CgfFormat.UVER_CRYSIS}. Preserves the stream position.

        Deprecated.

        :param stream: The stream from which to read.
        :type stream: file
        :return: A pair (version, user_version).
            The returned version is -1 if the file type or chunk table version
            is not supported, and -2 if the file is not a cgf file.
        @deprecated: Use CgfFormat.Data.inspect instead.
        """
        warnings.warn("use CgfFormat.Data.inspect", DeprecationWarning)
        data = cls.Data()
        try:
            data.inspectVersionOnly(stream)
        except ValueError:
            return -2, 0
        else:
            return data.version(), data.user_version()

    @classmethod
    def getGame(cls, version=None, user_version=None):
        """Guess game based on version and user_version. This is the inverse of
        L{getGameVersion}.

        :param version: The version as obtained by L{getVersion}.
        :type version: int
        :param user_version: The user version as obtained by L{getVersion}.
        :type user_version: int
        :return: 'Crysis' or 'Far Cry'
        @deprecated: Use L{CgfFormat.Data.game} instead.
        """
        warnings.warn("use CgfFormat.Data.game", DeprecationWarning)
        try:
            return {cls.UVER_FARCRY: "Far Cry",
                    cls.UVER_CRYSIS: "Crysis"}[user_version]
        except KeyError:
            raise ValueError("unknown version 0x%08X and user version %i" %
                             (version, user_version))

    @classmethod
    def getGameVersion(cls, game=None):
        """Get version and user_version for a particular game. This is the
        inverse of L{getGame}.

        :param game: 'Crysis' or 'Far Cry'.
        :type game: str
        :return: The version and user version.
        @deprecated: Use the version() and user_version() functions instead.

        >>> CgfFormat.getGameVersion("Far Cry")
        (1860, 1)
        >>> CgfFormat.getGameVersion("Crysis")
        (1860, 2)
        """
        if game == "Far Cry":
            return cls.VER_FARCRY, cls.UVER_FARCRY
        elif game == "Crysis":
            return cls.VER_CRYSIS, cls.UVER_CRYSIS
        else:
            raise ValueError("unknown game %s" % game)

    @classmethod
    def getFileType(cls, stream, version = None, user_version = None):
        """Returns file type (geometry or animation). Preserves the stream
        position.

        :param stream: The stream from which to read.
        :type stream: file
        :param version: The version as obtained by L{getVersion}.
        :type version: int
        :param user_version: The user version as obtained by L{getVersion}.
        :type user_version: int
        :return: L{FileType.GEOM} or L{FileType.ANIM}
        @deprecated: Use L{CgfFormat.Data.header.type} instead.
        """
        warnings.warn("use CgfFormat.Data.header.type", DeprecationWarning)
        pos = stream.tell()
        try:
            signat = stream.read(8)
            filetype, = struct.unpack('<I',
                                      stream.read(4))
        finally:
            stream.seek(pos)
        return filetype

    @classmethod
    def read(cls, stream, version=None, user_version=None,
             verbose=0, validate=True):
        """@deprecated: Use L{CgfFormat.Data.read} instead."""
        warnings.warn("use CgfFormat.Data.read", DeprecationWarning)
        data = cls.Data()
        data.read(stream)
        return data.header.type, data.chunks, data.versions

    @classmethod
    def write(cls, stream, version = None, user_version = None,
              filetype = None, chunks = None, versions = None,
              verbose = 0):
        """@deprecated: Use L{CgfFormat.Data.write} instead."""
        warnings.warn("use CgfFormat.Data.write", DeprecationWarning)
        data = cls.Data()
        data.header.type = filetype
        data.header.version = version
        data.chunks = chunks
        data.versions = versions
        data.game = cls.getGame(version=version, user_version=user_version)
        return data.write(stream)
    
    @classmethod
    def getChunkVersions(cls, version = None, user_version = None,
                         chunks = None):
        """Return version of each chunk in the chunk list for the
        given file version and file user version.

        :param version: The version.
        :type version: int
        :param user_version: The user version.
        :type user_version: int
        :param chunks: List of chunks.
        :type chunks: list of L{CgfFormat.Chunk}
        :return: Version of each chunk as list of ints (same length as
            C{chunks}).
        @deprecated: Use L{Data.update_versions} instead.
        """
        warnings.warn("use CgfFormat.Data.update_versions", DeprecationWarning)

        # game string
        game = cls.getGame(version = version, user_version = user_version)

        try:
            return [max(chunk.getVersions(game)) for chunk in chunks]
        except KeyError:
            raise cls.CgfError("game %s not supported" % game)

    @classmethod
    def getRoots(cls, *readresult):
        """Returns list of all root blocks. Used by L{PyFFI.qskope}
        and L{PyFFI.spells}.

        :param readresult: Result from L{walk} or L{read}.
        :type readresult: tuple
        :return: list of root blocks
        @deprecated: This function simply returns an empty list, and will eventually be removed.
        """
        warnings.warn("do not use the getRoots function", DeprecationWarning)
        return []

    @classmethod
    def getBlocks(cls, *readresult):
        """Returns list of all blocks. Used by L{PyFFI.qskope}
        and L{PyFFI.spells}.

        :param readresult: Result from L{walk} or L{read}.
        :type readresult: tuple
        :return: list of blocks
        @deprecated: Use L{Data.chunks} instead.
        """
        warnings.warn("use CgfFormat.Data.chunks", DeprecationWarning)
        return readresult[1]

    class Data(PyFFI.object_models.FileFormat.Data):
        """A class to contain the actual nif data.

        Note that L{versions} and L{chunk_table} are not automatically kept
        in sync with the L{chunks}, but they are
        resynchronized when calling L{write}.

        :ivar game: The cgf game.
        :type game: ``int``
        :ivar header: The nif header.
        :type header: L{CgfFormat.Header}
        :ivar chunks: List of chunks (the actual data).
        :type chunks: ``list`` of L{CgfFormat.Chunk}
        :ivar versions: List of chunk versions.
        :type versions: ``list`` of L{int}
        """

        class VersionUInt(PyFFI.object_models.Common.UInt):
            def setValue(self, value):
                if value is None:
                    self._value = None
                else:
                    PyFFI.object_models.Common.UInt.setValue(self, value)

            def __str__(self):
                if self._value is None:
                    return "None"
                else:
                    return "0x%08X" % self.getValue()

            def getDetailDisplay(self):
                return self.__str__()

        def __init__(self, filetype=0xffff0000, game="Far Cry"):
            # 0xffff0000 = CgfFormat.FileType.GEOM

            """Initialize cgf data. By default, this creates an empty
            cgf document of the given filetype and game.

            :param filetype: The file type (animation, or geometry).
            :type filetype: ``int``
            :param game: The game.
            :type game: ``str``
            """
            # create new header
            self.header = CgfFormat.Header()
            self.header.type = filetype
            self.header.version = 0x744 # no other chunk table versions
            # empty list of chunks
            self.chunks = []
            # empty list of versions (one per chunk)
            self.versions = []
            # chunk table
            self.chunk_table = CgfFormat.ChunkTable()
            # game
            # TODO store this in a way that can be displayed by qskope
            self.game = game

        # new functions

        def version(self):
            return self.header.version

        def user_version(self):
            if self.game == "Far Cry":
                return CgfFormat.UVER_FARCRY
            elif self.game == "Crysis":
                return CgfFormat.UVER_CRYSIS
            else:
                raise ValueError("unknown game %s" % game)

        def inspectVersionOnly(self, stream):
            """This function checks the version only, and is faster
            than the usual inspect function (which reads the full
            chunk table). Sets the L{header} and L{game} instance
            variables if the stream contains a valid cgf file.

            Call this function if you simply wish to check that a file is
            a cgf file without having to parse even the header.

            :param stream: The stream from which to read.
            :type stream: ``file``
            @raise C{ValueError}: If the stream does not contain a cgf file.
            """
            pos = stream.tell()
            try:
                signat = stream.read(8)
                filetype, version, offset = struct.unpack('<III',
                                                          stream.read(12))
            except IOError:
                raise
            except StandardError:
                # something went wrong with unpack
                # this means that the file is less than 20 bytes
                # cannot be a cgf file
                raise ValueError
            finally:
                stream.seek(pos)

            # test the data
            if signat[:6] != "CryTek":
                raise ValueError
            if filetype not in (CgfFormat.FileType.GEOM,
                                CgfFormat.FileType.ANIM):
                raise ValueError
            if version not in CgfFormat.versions.values():
                raise ValueError
            # quick and lame game check:
            # far cry has chunk table at the end, crysis at the start
            if offset == 0x14:
                self.game = "Crysis"
            else:
                self.game = "Far Cry"
            # load the actual header
            try:
                self.header.read(stream)
            finally:
                stream.seek(pos)

        # GlobalNode

        def getGlobalChildNodes(self, edge_filter=EdgeFilter()):
            """Returns chunks without parent."""
            # calculate all children of all chunks
            children = set()
            for chunk in self.chunks:
                children |= set(chunk.getGlobalChildNodes())
            # iterate over all chunks that are NOT in the list of children
            return (chunk for chunk in self.chunks
                    if not chunk in children)

        # DetailNode

        def replaceGlobalNode(self, oldbranch, newbranch,
                              edge_filter=EdgeFilter()):
            for i, chunk in enumerate(self.chunks):
                if chunk is oldbranch:
                    self.chunks[i] = newbranch
                else:
                    chunk.replaceGlobalNode(oldbranch, newbranch,
                                            edge_filter=edge_filter)

        def getDetailChildNodes(self, edge_filter=EdgeFilter()):
            yield self.header
            yield self.chunk_table

        def getDetailChildNames(self, edge_filter=EdgeFilter()):
            yield "header"
            yield "chunk table"

        # overriding PyFFI.object_models.FileFormat.Data methods

        def inspect(self, stream):
            """Quickly checks whether the stream appears to contain
            cgf data, and read the cgf header and chunk table. Resets stream to
            original position.

            Call this function if you only need to inspect the header and
            chunk table.

            :param stream: The file to inspect.
            :type stream: ``file``
            """
            logger = logging.getLogger("pyffi.cgf.data")
            pos = stream.tell()
            try:
                logger.debug("Reading header at 0x%08X." % stream.tell())
                self.inspectVersionOnly(stream)
                self.header.read(stream)
                stream.seek(self.header.offset)
                logger.debug("Reading chunk table version 0x%08X at 0x%08X." % (self.header.version, stream.tell()))
                self.chunk_table.read(
                    stream,
                    version=self.version(),
                    user_version=self.user_version())
            finally:
                stream.seek(pos)

        def read(self, stream):
            """Read a cgf file. Does not reset stream position.

            :param stream: The stream from which to read.
            :type stream: ``file``
            """
            validate = True # whether we validate on reading
            
            logger = logging.getLogger("pyffi.cgf.data")
            self.inspect(stream)
            version = self.version()
            user_version = self.user_version()

            # is it a caf file? these are missing chunk headers on controllers
            # (note: stream.name may not be a python string for some file
            # implementations, notably PyQt4, so convert it explicitely)
            is_caf = (str(stream.name)[-4:].lower() == ".caf")

            chunk_types = [
                chunk_type for chunk_type in dir(CgfFormat.ChunkType) \
                if chunk_type[:2] != '__']

            # get the chunk sizes (for double checking that we have all data)
            if validate:
                chunk_offsets = [chunkhdr.offset
                                 for chunkhdr in self.chunk_table.chunkHeaders]
                chunk_offsets.append(self.header.offset)
                chunk_sizes = []
                for chunkhdr in self.chunk_table.chunkHeaders:
                    next_chunk_offsets = [offset for offset in chunk_offsets
                                          if offset > chunkhdr.offset]
                    if next_chunk_offsets:
                        chunk_sizes.append(min(next_chunk_offsets) - chunkhdr.offset)
                    else:
                        stream.seek(0, 2)
                        chunk_sizes.append(stream.tell() - chunkhdr.offset)

            # read the chunks
            link_stack = [] # list of chunk identifiers, as added to the stack
            chunk_dct = {} # maps chunk index to actual chunk
            self.chunks = [] # records all chunks as read from cgf file in proper order
            self.versions = [] # records all chunk versions as read from cgf file
            for chunknum, chunkhdr in enumerate(self.chunk_table.chunkHeaders):
                # check that id is unique
                if chunkhdr.id in chunk_dct:
                    raise ValueError('chunk id %i not unique'%chunkhdr.id)

                # get chunk type
                for chunk_type in chunk_types:
                    if getattr(CgfFormat.ChunkType, chunk_type) == chunkhdr.type:
                        break
                else:
                    raise ValueError('unknown chunk type 0x%08X'%chunkhdr.type)
                try:
                    chunk = getattr(CgfFormat, '%sChunk' % chunk_type)()
                except AttributeError:
                    raise ValueError(
                        'undecoded chunk type 0x%08X (%sChunk)'
                        %(chunkhdr.type, chunk_type))
                # check the chunk version
                if not self.game in chunk.getGames():
                    raise ValueError(
                        'game %s does not support %sChunk'
                        % (self.game, chunk_type))
                if not chunkhdr.version in chunk.getVersions(self.game):
                    raise ValueError(
                        'chunk version 0x%08X not supported for game %s and %sChunk'
                        % (chunkhdr.version, self.game, chunk_type))

                # now read the chunk
                stream.seek(chunkhdr.offset)
                logger.debug("Reading %s chunk version 0x%08X at 0x%08X" % (chunk_type, chunkhdr.version, stream.tell()))

                # in far cry, most chunks start with a copy of chunkhdr
                # in crysis, more chunks start with chunkhdr
                # caf files are special: they don't have headers on controllers
                if not(user_version == CgfFormat.UVER_FARCRY
                       and chunkhdr.type in [
                           CgfFormat.ChunkType.SourceInfo,
                           CgfFormat.ChunkType.BoneNameList,
                           CgfFormat.ChunkType.BoneLightBinding,
                           CgfFormat.ChunkType.BoneInitialPos,
                           CgfFormat.ChunkType.MeshMorphTarget]) \
                    and not(user_version == CgfFormat.UVER_CRYSIS
                            and chunkhdr.type in [
                                CgfFormat.ChunkType.BoneNameList,
                                CgfFormat.ChunkType.BoneInitialPos]) \
                    and not(is_caf
                            and chunkhdr.type in [
                                CgfFormat.ChunkType.Controller]):
                    chunkhdr_copy = CgfFormat.ChunkHeader()
                    chunkhdr_copy.read(stream,
                                       version = version,
                                       user_version = user_version)
                    # check that the copy is valid
                    # note: chunkhdr_copy.offset != chunkhdr.offset check removed
                    # as many crysis cgf files have this wrong
                    if chunkhdr_copy.type != chunkhdr.type \
                       or chunkhdr_copy.version != chunkhdr.version \
                       or chunkhdr_copy.id != chunkhdr.id:
                        raise ValueError(
                            'chunk starts with invalid header:\n\
expected\n%sbut got\n%s'%(chunkhdr, chunkhdr_copy))
                else:
                    chunkhdr_copy = None

                chunk.read(
                    stream,
                    version = chunkhdr.version,
                    user_version = user_version,
                    link_stack = link_stack)
                self.chunks.append(chunk)
                self.versions.append(chunkhdr.version)
                chunk_dct[chunkhdr.id] = chunk

                if validate:
                    # calculate size
                    size = chunk.getSize(version = chunkhdr.version,
                                         user_version = user_version)
                    # take into account header copy
                    if chunkhdr_copy:
                        size += chunkhdr_copy.getSize(version = version,
                                                      user_version = user_version)
                    # check with number of bytes read
                    if size != stream.tell() - chunkhdr.offset:
                        logger.error("""\
getSize returns wrong size when reading %s at 0x%08X
actual bytes read is %i, getSize yields %i (expected %i bytes)"""
                                    % (chunk.__class__.__name__,
                                       chunkhdr.offset,
                                       size,
                                       stream.tell() - chunkhdr.offset,
                                       chunk_sizes[chunknum]))
                    # check for padding bytes
                    if chunk_sizes[chunknum] & 3 == 0:
                        padlen = ((4 - size & 3) & 3)
                        #assert(stream.read(padlen) == '\x00' * padlen)
                        size += padlen
                    # check size
                    if size != chunk_sizes[chunknum]:
                        logger.warn("""\
chunk size mismatch when reading %s at 0x%08X
%i bytes available, but actual bytes read is %i"""
                                    % (chunk.__class__.__name__,
                                       chunkhdr.offset,
                                       chunk_sizes[chunknum], size))

            # fix links
            for chunk, chunkversion in zip(self.chunks, self.versions):
                #print(chunk.__class__)
                chunk.fixLinks(
                    version=chunkversion, user_version=user_version,
                    block_dct=chunk_dct, link_stack=link_stack)
            if link_stack != []:
                raise CgfFormat.CgfError(
                    'not all links have been popped from the stack (bug?)')

        def write(self, stream):
            """Write a nif file. The L{header} and L{chunk_table} are
            recalculated from L{chunks}. Returns number of padding bytes
            written (this is for debugging purposes only).

            :param stream: The stream to which to write.
            :type stream: file
            :return: Number of padding bytes written.
            """
            logger = logging.getLogger("pyffi.cgf.data")
            # is it a caf file? these are missing chunk headers on controllers
            is_caf = (stream.name[-4:].lower() == ".caf")

            # variable to track number of padding bytes
            total_padding = 0

            # sanity check on version
            version = self.version()
            user_version = self.user_version()

            # chunk versions
            self.update_versions()

            # write header
            hdr_pos = stream.tell()
            self.header.offset = -1 # is set at the end
            self.header.write(
                stream, version=self.header.version, user_version=user_version)

            # chunk id is simply its index in the chunks list
            block_index_dct = dict((chunk, i)
                                   for i, chunk in enumerate(self.chunks))

            # write chunks and add headers to chunk table
            self.chunk_table = CgfFormat.ChunkTable()
            self.chunk_table.numChunks = len(self.chunks)
            self.chunk_table.chunkHeaders.updateSize()
            #print(self.chunk_table) # DEBUG

            # crysis: write chunk table now
            if user_version == CgfFormat.UVER_CRYSIS:
                self.header.offset = stream.tell()
                self.chunk_table.write(stream,
                            version=version, user_version=user_version)

            for chunkhdr, chunk, chunkversion in zip(self.chunk_table.chunkHeaders,
                                                     self.chunks, self.versions):
                logger.debug("Writing %s chunk version 0x%08X at 0x%08X" % (chunk.__class__.__name__, chunkhdr.version, stream.tell()))

                # set up chunk header
                chunkhdr.type = getattr(
                    CgfFormat.ChunkType, chunk.__class__.__name__[:-5])
                chunkhdr.version = chunkversion
                chunkhdr.offset = stream.tell()
                chunkhdr.id = block_index_dct[chunk]
                # write chunk header
                if not(user_version == CgfFormat.UVER_FARCRY
                       and chunkhdr.type in [
                           CgfFormat.ChunkType.SourceInfo,
                           CgfFormat.ChunkType.BoneNameList,
                           CgfFormat.ChunkType.BoneLightBinding,
                           CgfFormat.ChunkType.BoneInitialPos,
                           CgfFormat.ChunkType.MeshMorphTarget]) \
                    and not(user_version == CgfFormat.UVER_CRYSIS
                            and chunkhdr.type in [
                                CgfFormat.ChunkType.BoneNameList,
                                CgfFormat.ChunkType.BoneInitialPos]) \
                    and not(is_caf
                            and chunkhdr.type in [
                                CgfFormat.ChunkType.Controller]):
                    #print(chunkhdr) # DEBUG
                    chunkhdr.write(stream,
                                   version = version,
                                   user_version = user_version)
                # write chunk
                chunk.write(
                    stream, version = chunkversion, user_version = user_version,
                    block_index_dct = block_index_dct)
                # write padding bytes to align blocks
                padlen = (4 - stream.tell() & 3) & 3
                if padlen:
                    stream.write( "\x00" * padlen )
                    total_padding += padlen

            # write/update chunk table
            logger.debug("Writing chunk table version 0x%08X at 0x%08X" % (self.header.version, stream.tell()))
            if user_version == CgfFormat.UVER_CRYSIS:
                end_pos = stream.tell()
                stream.seek(self.header.offset)
                self.chunk_table.write(
                    stream, version=self.header.version, user_version=user_version)
            else:
                self.header.offset = stream.tell()
                self.chunk_table.write(
                    stream, version=self.header.version, user_version=user_version)
                end_pos = stream.tell()

            # update header
            stream.seek(hdr_pos)
            self.header.write(stream, version=version, user_version=user_version)

            # seek end of written data
            stream.seek(end_pos)

            # return number of padding bytes written
            return total_padding

        def update_versions(self):
            """Update L{versions} for the given chunks and game."""
            try:
                self.versions = [max(chunk.getVersions(self.game))
                                 for chunk in self.chunks]
            except KeyError:
                raise CgfFormat.CgfError("game %s not supported" % self.game)

    # extensions of generated structures

    class Chunk:
        def tree(self, block_type = None, follow_all = True):
            """A generator for parsing all blocks in the tree (starting from and
            including C{self}).

            :param block_type: If not ``None``, yield only blocks of the type C{block_type}.
            :param follow_all: If C{block_type} is not ``None``, then if this is ``True`` the function will parse the whole tree. Otherwise, the function will not follow branches that start by a non-C{block_type} block."""
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

        def applyScale(self, scale):
            """Apply scale factor on data."""
            pass

    class ChunkTable:
        def getChunkTypes(self):
            """Iterate all chunk types (in the form of Python classes) referenced
            in this table.
            """
            return (CgfFormat.CHUNK_MAP[chunk_header.type]
                    for chunk_header in self.chunkHeaders)

    class BoneInitialPosChunk:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < CgfFormat.EPSILON:
                return
            for mat in self.initialPosMatrices:
                mat.pos.x *= scale
                mat.pos.y *= scale
                mat.pos.z *= scale

        def getGlobalNodeParent(self):
            """Get the block parent (used for instance in the QSkope global
            view)."""
            return self.mesh

    class DataStreamChunk:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < CgfFormat.EPSILON:
                return
            for vert in self.vertices:
                vert.x *= scale
                vert.y *= scale
                vert.z *= scale

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
            return(
                "[ %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f ]\n[ %6.3f %6.3f %6.3f ]\n"
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
            if  (abs(self.m11 - 1.0) > CgfFormat.EPSILON
                 or abs(self.m12) > CgfFormat.EPSILON
                 or abs(self.m13) > CgfFormat.EPSILON
                 or abs(self.m21) > CgfFormat.EPSILON
                 or abs(self.m22 - 1.0) > CgfFormat.EPSILON
                 or abs(self.m23) > CgfFormat.EPSILON
                 or abs(self.m31) > CgfFormat.EPSILON
                 or abs(self.m32) > CgfFormat.EPSILON
                 or abs(self.m33 - 1.0) > CgfFormat.EPSILON):
                return False
            else:
                return True

        def getCopy(self):
            """Return a copy of the matrix."""
            mat = CgfFormat.Matrix33()
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
            mat = CgfFormat.Matrix33()
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
            # NOTE: 0.01 instead of CgfFormat.EPSILON to work around bad nif files

            # calculate self * self^T
            # this should correspond to
            # (scale * rotation) * (scale * rotation)^T
            # = scale * rotation * rotation^T * scale^T
            # = scale * scale^T
            self_transpose = self.getTranspose()
            mat = self * self_transpose

            # off diagonal elements should be zero
            if (abs(mat.m12) + abs(mat.m13)
                + abs(mat.m21) + abs(mat.m23)
                + abs(mat.m31) + abs(mat.m32)) > 0.01:
                return False

            return True

        def isRotation(self):
            """Returns ``True`` if the matrix is a rotation matrix
            (a member of SO(3))."""
            # NOTE: 0.01 instead of CgfFormat.EPSILON to work around bad nif files

            if not self.isScaleRotation():
                return False
            scale = self.getScale()
            if abs(scale.x - 1.0) > 0.01 \
               or abs(scale.y - 1.0) > 0.01 \
               or abs(scale.z - 1.0) > 0.01:
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
            # calculate self * self^T
            # this should correspond to
            # (rotation * scale)* (rotation * scale)^T
            # = scale * scale^T
            # = diagonal matrix with scales squared on the diagonal
            mat = self * self.getTranspose()

            scale = CgfFormat.Vector3()
            scale.x = mat.m11 ** 0.5
            scale.y = mat.m22 ** 0.5
            scale.z = mat.m33 ** 0.5

            if self.getDeterminant() < 0:
                return -scale
            else:
                return scale

        def getScaleRotation(self):
            """Decompose the matrix into scale and rotation, where scale is a float
            and rotation is a C{Matrix33}. Returns a pair (scale, rotation)."""
            rot = self.getCopy()
            scale = self.getScale()
            if min(abs(x) for x in scale.asTuple()) < CgfFormat.EPSILON:
                raise ZeroDivisionError('scale is zero, unable to obtain rotation')
            rot.m11 /= scale.x
            rot.m12 /= scale.x
            rot.m13 /= scale.x
            rot.m21 /= scale.y
            rot.m22 /= scale.y
            rot.m23 /= scale.y
            rot.m31 /= scale.z
            rot.m32 /= scale.z
            rot.m33 /= scale.z
            return (scale, rot)

        def setScaleRotation(self, scale, rotation):
            """Compose the matrix as the product of scale * rotation."""
            if not isinstance(scale, CgfFormat.Vector3):
                raise TypeError('scale must be Vector3')
            if not isinstance(rotation, CgfFormat.Matrix33):
                raise TypeError('rotation must be Matrix33')

            if not rotation.isRotation():
                raise ValueError('rotation must be rotation matrix')

            self.m11 = rotation.m11 * scale.x
            self.m12 = rotation.m12 * scale.x
            self.m13 = rotation.m13 * scale.x
            self.m21 = rotation.m21 * scale.y
            self.m22 = rotation.m22 * scale.y
            self.m23 = rotation.m23 * scale.y
            self.m31 = rotation.m31 * scale.z
            self.m32 = rotation.m32 * scale.z
            self.m33 = rotation.m33 * scale.z

        def getScaleQuat(self):
            """Decompose matrix into scale and quaternion."""
            scale, rot = self.getScaleRotation()
            quat = CgfFormat.Quat()
            trace = 1.0 + rot.m11 + rot.m22 + rot.m33

            if trace > CgfFormat.EPSILON:
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
            scale = self.getScale()
            mat = self.getTranspose()
            mat.m11 /= scale.x ** 2
            mat.m12 /= scale.x ** 2
            mat.m13 /= scale.x ** 2
            mat.m21 /= scale.y ** 2
            mat.m22 /= scale.y ** 2
            mat.m23 /= scale.y ** 2
            mat.m31 /= scale.z ** 2
            mat.m32 /= scale.z ** 2
            mat.m33 /= scale.z ** 2

        def __mul__(self, rhs):
            if isinstance(rhs, (float, int, long)):
                mat = CgfFormat.Matrix33()
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
            elif isinstance(rhs, CgfFormat.Vector3):
                raise TypeError("matrix*vector not supported;\
        please use left multiplication (vector*matrix)")
            elif isinstance(rhs, CgfFormat.Matrix33):
                mat = CgfFormat.Matrix33()
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
                mat = CgfFormat.Matrix33()
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
            if not isinstance(mat, CgfFormat.Matrix33):
                raise TypeError(
                    "do not know how to compare Matrix33 and %s"%mat.__class__)
            if (abs(self.m11 - mat.m11) > CgfFormat.EPSILON
                or abs(self.m12 - mat.m12) > CgfFormat.EPSILON
                or abs(self.m13 - mat.m13) > CgfFormat.EPSILON
                or abs(self.m21 - mat.m21) > CgfFormat.EPSILON
                or abs(self.m22 - mat.m22) > CgfFormat.EPSILON
                or abs(self.m23 - mat.m23) > CgfFormat.EPSILON
                or abs(self.m31 - mat.m31) > CgfFormat.EPSILON
                or abs(self.m32 - mat.m32) > CgfFormat.EPSILON
                or abs(self.m33 - mat.m33) > CgfFormat.EPSILON):
                return False
            return True

        def __ne__(self, mat):
            return not self.__eq__(mat)

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
                '[ %6.3f %6.3f %6.3f %6.3f ]\n'
                '[ %6.3f %6.3f %6.3f %6.3f ]\n'
                '[ %6.3f %6.3f %6.3f %6.3f ]\n'
                '[ %6.3f %6.3f %6.3f %6.3f ]\n'
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
            if (abs(self.m11 - 1.0) > CgfFormat.EPSILON
                or abs(self.m12) > CgfFormat.EPSILON
                or abs(self.m13) > CgfFormat.EPSILON
                or abs(self.m14) > CgfFormat.EPSILON
                or abs(self.m21) > CgfFormat.EPSILON
                or abs(self.m22 - 1.0) > CgfFormat.EPSILON
                or abs(self.m23) > CgfFormat.EPSILON
                or abs(self.m24) > CgfFormat.EPSILON
                or abs(self.m31) > CgfFormat.EPSILON
                or abs(self.m32) > CgfFormat.EPSILON
                or abs(self.m33 - 1.0) > CgfFormat.EPSILON
                or abs(self.m34) > CgfFormat.EPSILON
                or abs(self.m41) > CgfFormat.EPSILON
                or abs(self.m42) > CgfFormat.EPSILON
                or abs(self.m43) > CgfFormat.EPSILON
                or abs(self.m44 - 1.0) > CgfFormat.EPSILON):
                return False
            else:
                return True

        def getCopy(self):
            """Create a copy of the matrix."""
            mat = CgfFormat.Matrix44()
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
            m = CgfFormat.Matrix33()
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
            if not isinstance(m, CgfFormat.Matrix33):
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
            t = CgfFormat.Vector3()
            t.x = self.m41
            t.y = self.m42
            t.z = self.m43
            return t

        def setTranslation(self, translation):
            """Returns lower left 1x3 part."""
            if not isinstance(translation, CgfFormat.Vector3):
                raise TypeError('argument must be Vector3')
            self.m41 = translation.x
            self.m42 = translation.y
            self.m43 = translation.z

        def isScaleRotationTranslation(self):
            if not self.getMatrix33().isScaleRotation(): return False
            if abs(self.m14) > CgfFormat.EPSILON: return False
            if abs(self.m24) > CgfFormat.EPSILON: return False
            if abs(self.m34) > CgfFormat.EPSILON: return False
            if abs(self.m44 - 1.0) > CgfFormat.EPSILON: return False
            return True

        def getScaleRotationTranslation(self):
            rotscl = self.getMatrix33()
            scale, rot = rotscl.getScaleRotation()
            trans = self.getTranslation()
            return (scale, rot, trans)

        def getScaleQuatTranslation(self):
            rotscl = self.getMatrix33()
            scale, quat = rotscl.getScaleQuat()
            trans = self.getTranslation()
            return (scale, quat, trans)

        def setScaleRotationTranslation(self, scale, rotation, translation):
            if not isinstance(scale, CgfFormat.Vector3):
                raise TypeError('scale must be Vector3')
            if not isinstance(rotation, CgfFormat.Matrix33):
                raise TypeError('rotation must be Matrix33')
            if not isinstance(translation, CgfFormat.Vector3):
                raise TypeError('translation must be Vector3')

            if not rotation.isRotation():
                logger = logging.getLogger("pyffi.cgf.matrix")
                mat = rotation * rotation.getTranspose()
                idmat = CgfFormat.Matrix33()
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

                n = CgfFormat.Matrix44()
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
                if abs(det) < CgfFormat.EPSILON:
                    raise ZeroDivisionError('cannot invert matrix:\n%s'%self)
                for i in xrange(4):
                    for j in xrange(4):
                        if (i+j) & 1:
                            nn[j][i] = -determinant(adjoint(m, i, j)) / det
                        else:
                            nn[j][i] = determinant(adjoint(m, i, j)) / det
                n = CgfFormat.Matrix44()
                n.setRows(*nn)
                return n

        def __mul__(self, x):
            if isinstance(x, (float, int, long)):
                m = CgfFormat.Matrix44()
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
            elif isinstance(x, CgfFormat.Vector3):
                raise TypeError("matrix*vector not supported; please use left multiplication (vector*matrix)")
            elif isinstance(x, CgfFormat.Vector4):
                raise TypeError("matrix*vector not supported; please use left multiplication (vector*matrix)")
            elif isinstance(x, CgfFormat.Matrix44):
                m = CgfFormat.Matrix44()
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
                m = CgfFormat.Matrix44()
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
            if not isinstance(m, CgfFormat.Matrix44):
                raise TypeError("do not know how to compare Matrix44 and %s"%m.__class__)
            if abs(self.m11 - m.m11) > CgfFormat.EPSILON: return False
            if abs(self.m12 - m.m12) > CgfFormat.EPSILON: return False
            if abs(self.m13 - m.m13) > CgfFormat.EPSILON: return False
            if abs(self.m14 - m.m14) > CgfFormat.EPSILON: return False
            if abs(self.m21 - m.m21) > CgfFormat.EPSILON: return False
            if abs(self.m22 - m.m22) > CgfFormat.EPSILON: return False
            if abs(self.m23 - m.m23) > CgfFormat.EPSILON: return False
            if abs(self.m24 - m.m24) > CgfFormat.EPSILON: return False
            if abs(self.m31 - m.m31) > CgfFormat.EPSILON: return False
            if abs(self.m32 - m.m32) > CgfFormat.EPSILON: return False
            if abs(self.m33 - m.m33) > CgfFormat.EPSILON: return False
            if abs(self.m34 - m.m34) > CgfFormat.EPSILON: return False
            if abs(self.m41 - m.m41) > CgfFormat.EPSILON: return False
            if abs(self.m42 - m.m42) > CgfFormat.EPSILON: return False
            if abs(self.m43 - m.m43) > CgfFormat.EPSILON: return False
            if abs(self.m44 - m.m44) > CgfFormat.EPSILON: return False
            return True

        def __ne__(self, m):
            return not self.__eq__(m)

        def __add__(self, x):
            if isinstance(x, (CgfFormat.Matrix44)):
                m = CgfFormat.Matrix44()
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
                m = CgfFormat.Matrix44()
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
            if isinstance(x, (CgfFormat.Matrix44)):
                m = CgfFormat.Matrix44()
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
                m = CgfFormat.Matrix44()
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

    class MeshChunk:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < CgfFormat.EPSILON:
                return
            for vert in self.vertices:
                vert.p.x *= scale
                vert.p.y *= scale
                vert.p.z *= scale

            self.minBound.x *= scale
            self.minBound.y *= scale
            self.minBound.z *= scale
            self.maxBound.x *= scale
            self.maxBound.y *= scale
            self.maxBound.z *= scale

        def getVertices(self):
            """Generator for all vertices."""
            if self.vertices:
                for vert in self.vertices:
                    yield vert.p
            elif self.verticesData:
                for vert in self.verticesData.vertices:
                    yield vert

        def getNormals(self):
            """Generator for all normals."""
            if self.vertices:
                for vert in self.vertices:
                    yield vert.n
            elif self.normalsData:
                for norm in self.normalsData.normals:
                    yield norm

        def getColors(self):
            """Generator for all vertex colors."""
            if self.vertexColors:
                for color in self.vertexColors:
                    # Far Cry has no alpha channel
                    yield (color.r, color.g, color.b, 255)
            elif self.colorsData:
                if self.colorsData.rgbColors:
                    for color in self.colorsData.rgbColors:
                        yield (color.r, color.g, color.b, 255)
                elif self.colorsData.rgbaColors:
                    for color in self.colorsData.rgbaColors:
                        yield (color.r, color.g, color.b, color.a)

        def getNumTriangles(self):
            """Get number of triangles."""
            if self.faces:
                return self.numFaces
            elif self.indicesData:
                return self.indicesData.numElements // 3
            else:
                return 0

        def getTriangles(self):
            """Generator for all triangles."""
            if self.faces:
                for face in self.faces:
                    yield face.v0, face.v1, face.v2
            elif self.indicesData:
                it = iter(self.indicesData.indices)
                while True:
                   yield it.next(), it.next(), it.next()

        def getMaterialIndices(self):
            """Generator for all materials (per triangle)."""
            if self.faces:
                for face in self.faces:
                    yield face.material
            elif self.meshSubsets:
                for meshsubset in self.meshSubsets.meshSubsets:
                    for i in xrange(meshsubset.numIndices // 3):
                        yield meshsubset.matId

        def getUVs(self):
            """Generator for all uv coordinates."""
            if self.uvs:
                for uv in self.uvs:
                    yield uv.u, uv.v
            elif self.uvsData:
                for uv in self.uvsData.uvs:
                    yield uv.u, 1.0 - uv.v # OpenGL fix!

        def getUVTriangles(self):
            """Generator for all uv triangles."""
            if self.uvFaces:
                for uvface in self.uvFaces:
                    yield uvface.t0, uvface.t1, uvface.t2
            elif self.indicesData:
                # Crysis: UV triangles coincide with triangles
                it = iter(self.indicesData.indices)
                while True:
                    yield it.next(), it.next(), it.next()

        ### DEPRECATED: USE setGeometry INSTEAD ###
        def setVerticesNormals(self, vertices, normals):
            """B{Deprecated. Use L{setGeometry} instead.} Set vertices and normals. This used to be the first function to call
            when setting mesh geometry data.

            Returns list of chunks that have been added."""
            # Far Cry
            self.numVertices = len(vertices)
            self.vertices.updateSize()

            # Crysis
            self.verticesData = CgfFormat.DataStreamChunk()
            self.verticesData.dataStreamType = CgfFormat.DataStreamType.VERTICES
            self.verticesData.bytesPerElement = 12
            self.verticesData.numElements = len(vertices)
            self.verticesData.vertices.updateSize()

            self.normalsData = CgfFormat.DataStreamChunk()
            self.normalsData.dataStreamType = CgfFormat.DataStreamType.NORMALS
            self.normalsData.bytesPerElement = 12
            self.normalsData.numElements = len(vertices)
            self.normalsData.normals.updateSize()

            # set vertex coordinates and normals for Far Cry
            for cryvert, vert, norm in izip(self.vertices, vertices, normals):
                cryvert.p.x = vert[0]
                cryvert.p.y = vert[1]
                cryvert.p.z = vert[2]
                cryvert.n.x = norm[0]
                cryvert.n.y = norm[1]
                cryvert.n.z = norm[2]

            # set vertex coordinates and normals for Crysis
            for cryvert, crynorm, vert, norm in izip(self.verticesData.vertices,
                                                     self.normalsData.normals,
                                                     vertices, normals):
                cryvert.x = vert[0]
                cryvert.y = vert[1]
                cryvert.z = vert[2]
                crynorm.x = norm[0]
                crynorm.y = norm[1]
                crynorm.z = norm[2]

        ### STILL WIP!!! ###
        def setGeometry(self,
                        verticeslist = None, normalslist = None,
                        triangleslist = None, matlist = None,
                        uvslist = None, colorslist = None):
            """Set geometry data.

            >>> from PyFFI.Formats.CGF import CgfFormat
            >>> chunk = CgfFormat.MeshChunk()
            >>> vertices1 = [(0,0,0),(0,1,0),(1,0,0),(1,1,0)]
            >>> vertices2 = [(0,0,1),(0,1,1),(1,0,1),(1,1,1)]
            >>> normals1 = [(0,0,-1),(0,0,-1),(0,0,-1),(0,0,-1)]
            >>> normals2 = [(0,0,1),(0,0,1),(0,0,1),(0,0,1)]
            >>> triangles1 = [(0,1,2),(2,1,3)]
            >>> triangles2 = [(0,1,2),(2,1,3)]
            >>> uvs1 = [(0,0),(0,1),(1,0),(1,1)]
            >>> uvs2 = [(0,0),(0,1),(1,0),(1,1)]
            >>> colors1 = [(0,1,2,3),(4,5,6,7),(8,9,10,11),(12,13,14,15)]
            >>> colors2 = [(50,51,52,53),(54,55,56,57),(58,59,60,61),(62,63,64,65)]
            >>> chunk.setGeometry(verticeslist = [vertices1, vertices2],
            ...                   normalslist = [normals1, normals2],
            ...                   triangleslist = [triangles1, triangles2],
            ...                   uvslist = [uvs1, uvs2],
            ...                   matlist = [2,5],
            ...                   colorslist = [colors1, colors2])
            >>> print(chunk) # doctest: +ELLIPSIS
            <class 'PyFFI.Formats.CGF.MeshChunk'> instance at ...
            * hasVertexWeights : False
            * hasVertexColors : True
            * inWorldSpace : False
            * reserved1 : 0
            * reserved2 : 0
            * flags1 : 0
            * flags2 : 0
            * numVertices : 8
            * numIndices : 12
            * numUvs : 8
            * numFaces : 4
            * material : None
            * numMeshSubsets : 2
            * meshSubsets : <class 'PyFFI.Formats.CGF.MeshSubsetsChunk'> instance at ...
            * vertAnim : None
            * vertices :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: <class 'PyFFI.Formats.CGF.Vertex'> instance at ...
                * p : [  0.000  0.000  0.000 ]
                * n : [  0.000  0.000 -1.000 ]
                1: <class 'PyFFI.Formats.CGF.Vertex'> instance at ...
                * p : [  0.000  1.000  0.000 ]
                * n : [  0.000  0.000 -1.000 ]
                2: <class 'PyFFI.Formats.CGF.Vertex'> instance at ...
                * p : [  1.000  0.000  0.000 ]
                * n : [  0.000  0.000 -1.000 ]
                3: <class 'PyFFI.Formats.CGF.Vertex'> instance at ...
                * p : [  1.000  1.000  0.000 ]
                * n : [  0.000  0.000 -1.000 ]
                4: <class 'PyFFI.Formats.CGF.Vertex'> instance at ...
                * p : [  0.000  0.000  1.000 ]
                * n : [  0.000  0.000  1.000 ]
                5: <class 'PyFFI.Formats.CGF.Vertex'> instance at ...
                * p : [  0.000  1.000  1.000 ]
                * n : [  0.000  0.000  1.000 ]
                6: <class 'PyFFI.Formats.CGF.Vertex'> instance at ...
                * p : [  1.000  0.000  1.000 ]
                * n : [  0.000  0.000  1.000 ]
                7: <class 'PyFFI.Formats.CGF.Vertex'> instance at ...
                * p : [  1.000  1.000  1.000 ]
                * n : [  0.000  0.000  1.000 ]
            * faces :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: <class 'PyFFI.Formats.CGF.Face'> instance at ...
                * v0 : 0
                * v1 : 1
                * v2 : 2
                * material : 2
                * smGroup : 1
                1: <class 'PyFFI.Formats.CGF.Face'> instance at ...
                * v0 : 2
                * v1 : 1
                * v2 : 3
                * material : 2
                * smGroup : 1
                2: <class 'PyFFI.Formats.CGF.Face'> instance at ...
                * v0 : 4
                * v1 : 5
                * v2 : 6
                * material : 5
                * smGroup : 1
                3: <class 'PyFFI.Formats.CGF.Face'> instance at ...
                * v0 : 6
                * v1 : 5
                * v2 : 7
                * material : 5
                * smGroup : 1
            * uvs :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 0.0
                * v : 0.0
                1: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 0.0
                * v : 1.0
                2: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 1.0
                * v : 0.0
                3: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 1.0
                * v : 1.0
                4: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 0.0
                * v : 0.0
                5: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 0.0
                * v : 1.0
                6: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 1.0
                * v : 0.0
                7: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 1.0
                * v : 1.0
            * uvFaces :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: <class 'PyFFI.Formats.CGF.UVFace'> instance at ...
                * t0 : 0
                * t1 : 1
                * t2 : 2
                1: <class 'PyFFI.Formats.CGF.UVFace'> instance at ...
                * t0 : 2
                * t1 : 1
                * t2 : 3
                2: <class 'PyFFI.Formats.CGF.UVFace'> instance at ...
                * t0 : 4
                * t1 : 5
                * t2 : 6
                3: <class 'PyFFI.Formats.CGF.UVFace'> instance at ...
                * t0 : 6
                * t1 : 5
                * t2 : 7
            * vertexColors :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: <class 'PyFFI.Formats.CGF.IRGB'> instance at ...
                * r : 0
                * g : 1
                * b : 2
                1: <class 'PyFFI.Formats.CGF.IRGB'> instance at ...
                * r : 4
                * g : 5
                * b : 6
                2: <class 'PyFFI.Formats.CGF.IRGB'> instance at ...
                * r : 8
                * g : 9
                * b : 10
                3: <class 'PyFFI.Formats.CGF.IRGB'> instance at ...
                * r : 12
                * g : 13
                * b : 14
                4: <class 'PyFFI.Formats.CGF.IRGB'> instance at ...
                * r : 50
                * g : 51
                * b : 52
                5: <class 'PyFFI.Formats.CGF.IRGB'> instance at ...
                * r : 54
                * g : 55
                * b : 56
                6: <class 'PyFFI.Formats.CGF.IRGB'> instance at ...
                * r : 58
                * g : 59
                * b : 60
                7: <class 'PyFFI.Formats.CGF.IRGB'> instance at ...
                * r : 62
                * g : 63
                * b : 64
            * verticesData : <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * normalsData : <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * uvsData : <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * colorsData : <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * colors2Data : None
            * indicesData : <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * tangentsData : <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * shCoeffsData : None
            * shapeDeformationData : None
            * boneMapData : None
            * faceMapData : None
            * vertMatsData : None
            * reservedData :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: None
                1: None
                2: None
                3: None
            * physicsData :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: None
                1: None
                2: None
                3: None
            * minBound : [  0.000  0.000  0.000 ]
            * maxBound : [  1.000  1.000  1.000 ]
            * reserved3 :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: 0
                1: 0
                2: 0
                3: 0
                4: 0
                5: 0
                6: 0
                7: 0
                8: 0
                9: 0
                10: 0
                11: 0
                12: 0
                13: 0
                14: 0
                15: 0
                16: 0
                etc...
            <BLANKLINE>
            >>> print(chunk.meshSubsets) # doctest: +ELLIPSIS
            <class 'PyFFI.Formats.CGF.MeshSubsetsChunk'> instance at ...
            * flags :
                <class 'PyFFI.Formats.CGF.MeshSubsetsFlags'> instance at ...
                * shHasDecomprMat : 0
                * boneIndices : 0
            * numMeshSubsets : 2
            * reserved1 : 0
            * reserved2 : 0
            * meshSubsets :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: <class 'PyFFI.Formats.CGF.MeshSubset'> instance at ...
                * firstIndex : 0
                * numIndices : 6
                * firstVertex : 0
                * numVertices : 4
                * matId : 2
                * radius : 0.7071067...
                * center : [  0.500  0.500  0.000 ]
                1: <class 'PyFFI.Formats.CGF.MeshSubset'> instance at ...
                * firstIndex : 6
                * numIndices : 6
                * firstVertex : 4
                * numVertices : 4
                * matId : 5
                * radius : 0.7071067...
                * center : [  0.500  0.500  1.000 ]
            <BLANKLINE>
            >>> print(chunk.verticesData) # doctest: +ELLIPSIS
            <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * flags : 0
            * dataStreamType : VERTICES
            * numElements : 8
            * bytesPerElement : 12
            * reserved1 : 0
            * reserved2 : 0
            * vertices :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: [  0.000  0.000  0.000 ]
                1: [  0.000  1.000  0.000 ]
                2: [  1.000  0.000  0.000 ]
                3: [  1.000  1.000  0.000 ]
                4: [  0.000  0.000  1.000 ]
                5: [  0.000  1.000  1.000 ]
                6: [  1.000  0.000  1.000 ]
                7: [  1.000  1.000  1.000 ]
            <BLANKLINE>
            >>> print(chunk.normalsData) # doctest: +ELLIPSIS
            <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * flags : 0
            * dataStreamType : NORMALS
            * numElements : 8
            * bytesPerElement : 12
            * reserved1 : 0
            * reserved2 : 0
            * normals :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: [  0.000  0.000 -1.000 ]
                1: [  0.000  0.000 -1.000 ]
                2: [  0.000  0.000 -1.000 ]
                3: [  0.000  0.000 -1.000 ]
                4: [  0.000  0.000  1.000 ]
                5: [  0.000  0.000  1.000 ]
                6: [  0.000  0.000  1.000 ]
                7: [  0.000  0.000  1.000 ]
            <BLANKLINE>
            >>> print(chunk.indicesData) # doctest: +ELLIPSIS
            <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * flags : 0
            * dataStreamType : INDICES
            * numElements : 12
            * bytesPerElement : 2
            * reserved1 : 0
            * reserved2 : 0
            * indices :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: 0
                1: 1
                2: 2
                3: 2
                4: 1
                5: 3
                6: 4
                7: 5
                8: 6
                9: 6
                10: 5
                11: 7
            <BLANKLINE>
            >>> print(chunk.uvsData) # doctest: +ELLIPSIS
            <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * flags : 0
            * dataStreamType : UVS
            * numElements : 8
            * bytesPerElement : 8
            * reserved1 : 0
            * reserved2 : 0
            * uvs :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 0.0
                * v : 1.0
                1: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 0.0
                * v : 0.0
                2: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 1.0
                * v : 1.0
                3: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 1.0
                * v : 0.0
                4: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 0.0
                * v : 1.0
                5: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 0.0
                * v : 0.0
                6: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 1.0
                * v : 1.0
                7: <class 'PyFFI.Formats.CGF.UV'> instance at ...
                * u : 1.0
                * v : 0.0
            <BLANKLINE>
            >>> print(chunk.tangentsData) # doctest: +ELLIPSIS
            <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * flags : 0
            * dataStreamType : TANGENTS
            * numElements : 8
            * bytesPerElement : 16
            * reserved1 : 0
            * reserved2 : 0
            * tangents :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0, 0: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 32767
                * y : 0
                * z : 0
                * w : 32767
                0, 1: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 0
                * y : -32767
                * z : 0
                * w : 32767
                1, 0: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 32767
                * y : 0
                * z : 0
                * w : 32767
                1, 1: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 0
                * y : -32767
                * z : 0
                * w : 32767
                2, 0: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 32767
                * y : 0
                * z : 0
                * w : 32767
                2, 1: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 0
                * y : -32767
                * z : 0
                * w : 32767
                3, 0: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 32767
                * y : 0
                * z : 0
                * w : 32767
                3, 1: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 0
                * y : -32767
                * z : 0
                * w : 32767
                4, 0: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 32767
                * y : 0
                * z : 0
                * w : 32767
                4, 1: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 0
                * y : -32767
                * z : 0
                * w : 32767
                5, 0: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 32767
                * y : 0
                * z : 0
                * w : 32767
                5, 1: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 0
                * y : -32767
                * z : 0
                * w : 32767
                6, 0: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 32767
                * y : 0
                * z : 0
                * w : 32767
                6, 1: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 0
                * y : -32767
                * z : 0
                * w : 32767
                7, 0: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 32767
                * y : 0
                * z : 0
                * w : 32767
                7, 1: <class 'PyFFI.Formats.CGF.Tangent'> instance at ...
                * x : 0
                * y : -32767
                * z : 0
                * w : 32767
            <BLANKLINE>
            >>> print(chunk.colorsData) # doctest: +ELLIPSIS
            <class 'PyFFI.Formats.CGF.DataStreamChunk'> instance at ...
            * flags : 0
            * dataStreamType : COLORS
            * numElements : 8
            * bytesPerElement : 4
            * reserved1 : 0
            * reserved2 : 0
            * rgbaColors :
                <class 'PyFFI.object_models.xml.Array.Array'> instance at ...
                0: <class 'PyFFI.Formats.CGF.IRGBA'> instance at ...
                * r : 0
                * g : 1
                * b : 2
                * a : 3
                1: <class 'PyFFI.Formats.CGF.IRGBA'> instance at ...
                * r : 4
                * g : 5
                * b : 6
                * a : 7
                2: <class 'PyFFI.Formats.CGF.IRGBA'> instance at ...
                * r : 8
                * g : 9
                * b : 10
                * a : 11
                3: <class 'PyFFI.Formats.CGF.IRGBA'> instance at ...
                * r : 12
                * g : 13
                * b : 14
                * a : 15
                4: <class 'PyFFI.Formats.CGF.IRGBA'> instance at ...
                * r : 50
                * g : 51
                * b : 52
                * a : 53
                5: <class 'PyFFI.Formats.CGF.IRGBA'> instance at ...
                * r : 54
                * g : 55
                * b : 56
                * a : 57
                6: <class 'PyFFI.Formats.CGF.IRGBA'> instance at ...
                * r : 58
                * g : 59
                * b : 60
                * a : 61
                7: <class 'PyFFI.Formats.CGF.IRGBA'> instance at ...
                * r : 62
                * g : 63
                * b : 64
                * a : 65
            <BLANKLINE>

            :param verticeslist: A list of lists of vertices (one list per material).
            :param normalslist: A list of lists of normals (one list per material).
            :param triangleslist: A list of lists of triangles (one list per material).
            :param matlist: A list of material indices. Optional.
            :param uvslist: A list of lists of uvs (one list per material). Optional.
            :param colorslist: A list of lists of RGBA colors (one list per material).
                Optional. Each color is a tuple (r, g, b, a) with each component an
                integer between 0 and 255.
            """
            # argument sanity checking
            # check length of lists
            if len(verticeslist) != len(normalslist):
                raise ValueError("normalslist must have same length as verticeslist")
            if len(triangleslist) != len(normalslist):
                raise ValueError("triangleslist must have same length as verticeslist")
            if not matlist is None and len(verticeslist) != len(matlist):
                raise ValueError("matlist must have same length as verticeslist")
            if not uvslist is None and len(verticeslist) != len(uvslist):
                raise ValueError("uvslist must have same length as verticeslist")
            if not colorslist is None and len(verticeslist) != len(colorslist):
                raise ValueError("colorslist must have same length as verticeslist")

            # check length of lists in lists
            for vertices, normals in izip(verticeslist, normalslist):
                if len(vertices) != len(normals):
                    raise ValueError("vertex and normal lists must have same length")
            if not uvslist is None:
                for vertices, uvs in izip(verticeslist, uvslist):
                    if len(vertices) != len(uvs):
                        raise ValueError("vertex and uv lists must have same length")
            if not colorslist is None:
                for vertices, colors in izip(verticeslist, colorslist):
                    if len(vertices) != len(colors):
                        raise ValueError("vertex and color lists must have same length")

            # get total number of vertices
            numvertices = sum(len(vertices) for vertices in verticeslist)
            if numvertices > 65535:
                raise ValueError("cannot store geometry: too many vertices (%i and maximum is 65535)" % numvertices)
            numtriangles = sum(len(triangles) for triangles in triangleslist)

            # Far Cry data preparation
            self.numVertices = numvertices
            self.vertices.updateSize()
            selfvertices_iter = iter(self.vertices)
            self.numFaces = numtriangles
            self.faces.updateSize()
            selffaces_iter = iter(self.faces)
            if not uvslist is None:
                self.numUvs = numvertices
                self.uvs.updateSize()
                self.uvFaces.updateSize()
                selfuvs_iter = iter(self.uvs)
                selfuvFaces_iter = iter(self.uvFaces)
            if not colorslist is None:
                self.hasVertexColors = True
                self.vertexColors.updateSize()
                selfvertexColors_iter = iter(self.vertexColors)

            # Crysis data preparation
            self.numIndices = numtriangles * 3

            self.verticesData = CgfFormat.DataStreamChunk()
            self.verticesData.dataStreamType = CgfFormat.DataStreamType.VERTICES
            self.verticesData.bytesPerElement = 12
            self.verticesData.numElements = numvertices
            self.verticesData.vertices.updateSize()
            selfverticesData_iter = iter(self.verticesData.vertices)

            self.normalsData = CgfFormat.DataStreamChunk()
            self.normalsData.dataStreamType = CgfFormat.DataStreamType.NORMALS
            self.normalsData.bytesPerElement = 12
            self.normalsData.numElements = numvertices
            self.normalsData.normals.updateSize()
            selfnormalsData_iter = iter(self.normalsData.normals)

            self.indicesData = CgfFormat.DataStreamChunk()
            self.indicesData.dataStreamType = CgfFormat.DataStreamType.INDICES
            self.indicesData.bytesPerElement = 2
            self.indicesData.numElements = numtriangles * 3
            self.indicesData.indices.updateSize()

            if not uvslist is None:
                # uvs
                self.uvsData = CgfFormat.DataStreamChunk()
                self.uvsData.dataStreamType = CgfFormat.DataStreamType.UVS
                self.uvsData.bytesPerElement = 8
                self.uvsData.numElements = numvertices
                self.uvsData.uvs.updateSize()
                selfuvsData_iter = iter(self.uvsData.uvs)
                # have tangent space
                has_tangentspace = True
            else:
                # no tangent space
                has_tangentspace = False

            if not colorslist is None:
                # vertex colors
                self.colorsData = CgfFormat.DataStreamChunk()
                self.colorsData.dataStreamType = CgfFormat.DataStreamType.COLORS
                self.colorsData.bytesPerElement = 4
                self.colorsData.numElements = numvertices
                self.colorsData.rgbaColors.updateSize()
                selfcolorsData_iter = iter(self.colorsData.rgbaColors)

            self.numMeshSubsets = len(verticeslist)
            self.meshSubsets = CgfFormat.MeshSubsetsChunk()
            self.meshSubsets.numMeshSubsets = self.numMeshSubsets
            self.meshSubsets.meshSubsets.updateSize()

            # set up default iterators
            if matlist is None:
                matlist = itertools.repeat(0)
            if uvslist is None:
                uvslist = itertools.repeat(None)
            if colorslist is None:
                colorslist = itertools.repeat(None)

            # now iterate over all materials
            firstvertexindex = 0
            firstindicesindex = 0
            for vertices, normals, triangles, mat, uvs, colors, meshsubset in izip(
                verticeslist, normalslist,
                triangleslist, matlist,
                uvslist, colorslist,
                self.meshSubsets.meshSubsets):

                # set Crysis mesh subset info
                meshsubset.firstIndex = firstindicesindex
                meshsubset.numIndices = len(triangles) * 3
                meshsubset.firstVertex = firstvertexindex
                meshsubset.numVertices = len(vertices)
                meshsubset.matId = mat
                center, radius = PyFFI.utils.math.getCenterRadius(vertices)
                meshsubset.radius = radius
                meshsubset.center.x = center[0]
                meshsubset.center.y = center[1]
                meshsubset.center.z = center[2]

                # set vertex coordinates and normals for Far Cry
                for vert, norm in izip(vertices, normals):
                    cryvert = selfvertices_iter.next()
                    cryvert.p.x = vert[0]
                    cryvert.p.y = vert[1]
                    cryvert.p.z = vert[2]
                    cryvert.n.x = norm[0]
                    cryvert.n.y = norm[1]
                    cryvert.n.z = norm[2]

                # set vertex coordinates and normals for Crysis
                for vert, norm in izip(vertices, normals):
                    cryvert = selfverticesData_iter.next()
                    crynorm = selfnormalsData_iter.next()
                    cryvert.x = vert[0]
                    cryvert.y = vert[1]
                    cryvert.z = vert[2]
                    crynorm.x = norm[0]
                    crynorm.y = norm[1]
                    crynorm.z = norm[2]

                # set Far Cry face info
                for triangle in triangles:
                    cryface = selffaces_iter.next()
                    cryface.v0 = triangle[0] + firstvertexindex
                    cryface.v1 = triangle[1] + firstvertexindex
                    cryface.v2 = triangle[2] + firstvertexindex
                    cryface.material = mat

                # set Crysis face info
                for i, vertexindex in enumerate(itertools.chain(*triangles)):
                    self.indicesData.indices[i + firstindicesindex] \
                        = vertexindex + firstvertexindex

                if not uvs is None:
                    # set Far Cry uv info
                    for triangle in triangles:
                        cryuvface = selfuvFaces_iter.next()
                        cryuvface.t0 = triangle[0] + firstvertexindex
                        cryuvface.t1 = triangle[1] + firstvertexindex
                        cryuvface.t2 = triangle[2] + firstvertexindex
                    for uv in uvs:
                        cryuv = selfuvs_iter.next()
                        cryuv.u = uv[0]
                        cryuv.v = uv[1]

                    # set Crysis uv info
                    for uv in uvs:
                        cryuv = selfuvsData_iter.next()
                        cryuv.u = uv[0]
                        cryuv.v = 1.0 - uv[1] # OpenGL fix

                if not colors is None:
                    # set Far Cry color info
                    for color in colors:
                        crycolor = selfvertexColors_iter.next()
                        crycolor.r = color[0]
                        crycolor.g = color[1]
                        crycolor.b = color[2]
                        # note: Far Cry does not support alpha color channel

                    # set Crysis color info
                    for color in colors:
                        crycolor = selfcolorsData_iter.next()
                        crycolor.r = color[0]
                        crycolor.g = color[1]
                        crycolor.b = color[2]
                        crycolor.a = color[3]

                # update index offsets
                firstvertexindex += len(vertices)
                firstindicesindex += 3 * len(triangles)

            # update tangent space
            if has_tangentspace:
                self.updateTangentSpace()

            # set global bounding box
            minbound, maxbound = PyFFI.utils.math.getBoundingBox(
                list(itertools.chain(*verticeslist)))
            self.minBound.x = minbound[0]
            self.minBound.y = minbound[1]
            self.minBound.z = minbound[2]
            self.maxBound.x = maxbound[0]
            self.maxBound.y = maxbound[1]
            self.maxBound.z = maxbound[2]

        def updateTangentSpace(self):
            """Recalculate tangent space data."""
            # set up tangent space
            self.tangentsData = CgfFormat.DataStreamChunk()
            self.tangentsData.dataStreamType = CgfFormat.DataStreamType.TANGENTS
            self.tangentsData.bytesPerElement = 16
            self.tangentsData.numElements = self.numVertices
            self.tangentsData.tangents.updateSize()
            selftangentsData_iter = iter(self.tangentsData.tangents)

            # set Crysis tangents info
            tangents, binormals, orientations = PyFFI.utils.tangentspace.getTangentSpace(
                vertices = list((vert.x, vert.y, vert.z)
                                for vert in self.verticesData.vertices),
                normals = list((norm.x, norm.y, norm.z)
                                for norm in self.normalsData.normals),
                uvs = list((uv.u, uv.v)
                           for uv in self.uvsData.uvs),
                triangles = list(self.getTriangles()),
                orientation = True)

            for crytangent, tan, bin, orient in izip(self.tangentsData.tangents,
                                                     tangents, binormals, orientations):
                if orient > 0:
                    tangent_w = 32767
                else:
                    tangent_w = -32767
                crytangent[1].x = int(32767 * tan[0])
                crytangent[1].y = int(32767 * tan[1])
                crytangent[1].z = int(32767 * tan[2])
                crytangent[1].w = tangent_w
                crytangent[0].x = int(32767 * bin[0])
                crytangent[0].y = int(32767 * bin[1])
                crytangent[0].z = int(32767 * bin[2])
                crytangent[0].w = tangent_w

    class MeshMorphTargetChunk:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < CgfFormat.EPSILON:
                return
            for morphvert in self.morphVertices:
                morphvert.vertexTarget.x *= scale
                morphvert.vertexTarget.y *= scale
                morphvert.vertexTarget.z *= scale

        def getGlobalNodeParent(self):
            """Get the block parent (used for instance in the QSkope global view)."""
            return self.mesh

        def getGlobalDisplay(self):
            """Return a name for the block."""
            return self.targetName

    class MeshSubsetsChunk:
        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < CgfFormat.EPSILON:
                return
            for meshsubset in self.meshSubsets:
                meshsubset.radius *= scale
                meshsubset.center.x *= scale
                meshsubset.center.y *= scale
                meshsubset.center.z *= scale

    class MtlChunk:
        def getNameShaderScript(self):
            """Extract name, shader, and script."""
            name = self.name
            shader_begin = name.find("(")
            shader_end = name.find(")")
            script_begin = name.find("/")
            if (script_begin != -1):
                if (name.count("/") != 1):
                    # must have exactly one script
                    raise ValueError("%s malformed, has multiple ""/"""%name)
                mtlscript = name[script_begin+1:]
            else:
                mtlscript = ""
            if (shader_begin != -1): # if a shader was specified
                mtl_end = shader_begin
                # must have exactly one shader
                if (name.count("(") != 1):
                    # some names are buggy and have "((" instead of "("
                    # like in jungle_camp_sleeping_barack
                    # here we handle that case
                    if name[shader_begin + 1] == "(" \
                       and name[shader_begin + 1:].count("(") == 1:
                        shader_begin += 1
                    else:
                        raise ValueError("%s malformed, has multiple ""("""%name)
                if (name.count(")") != 1):
                    raise ValueError("%s malformed, has multiple "")"""%name)
                # shader name should non-empty
                if shader_begin > shader_end:
                    raise ValueError("%s malformed, ""("" comes after "")"""%name)
                # script must be immediately followed by the material
                if (script_begin != -1) and (shader_end + 1 != script_begin):
                    raise ValueError("%s malformed, shader not followed by script"%name)
                mtlname = name[:mtl_end]
                mtlshader = name[shader_begin+1:shader_end]
            else:
                if script_begin != -1:
                    mtlname = name[:script_begin]
                else:
                    mtlname = name[:]
                mtlshader = ""
            return mtlname, mtlshader, mtlscript

    class NodeChunk:
        def getGlobalNodeParent(self):
            """Get the block parent (used for instance in the QSkope global view)."""
            return self.parent

        def applyScale(self, scale):
            """Apply scale factor on data."""
            if abs(scale - 1.0) < CgfFormat.EPSILON:
                return
            self.transform.m41 *= scale
            self.transform.m42 *= scale
            self.transform.m43 *= scale
            self.pos.x *= scale
            self.pos.y *= scale
            self.pos.z *= scale

        def updatePosRotScl(self):
            """Update position, rotation, and scale, from the transform."""
            scale, quat, trans = self.transform.getScaleQuatTranslation()
            self.pos.x = trans.x
            self.pos.y = trans.y
            self.pos.z = trans.z
            self.rot.x = quat.x
            self.rot.y = quat.y
            self.rot.z = quat.z
            self.rot.w = quat.w
            self.scl.x = scale.x
            self.scl.y = scale.y
            self.scl.z = scale.z

    class SourceInfoChunk:
        def getGlobalDisplay(self):
            """Return a name for the block."""
            idx = max(self.sourceFile.rfind("\\"), self.sourceFile.rfind("/"))
            return self.sourceFile[idx+1:]

    class TimingChunk:
        def getGlobalDisplay(self):
            """Return a name for the block."""
            return self.globalRange.name

    class Vector3:
        def asList(self):
            return [self.x, self.y, self.z]

        def asTuple(self):
            return (self.x, self.y, self.z)

        def norm(self):
            return (self.x*self.x + self.y*self.y + self.z*self.z) ** 0.5

        def normalize(self):
            norm = self.norm()
            if norm < CgfFormat.EPSILON:
                raise ZeroDivisionError('cannot normalize vector %s'%self)
            self.x /= norm
            self.y /= norm
            self.z /= norm

        def getCopy(self):
            v = CgfFormat.Vector3()
            v.x = self.x
            v.y = self.y
            v.z = self.z
            return v

        def __str__(self):
            return "[ %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z)

        def __mul__(self, x):
            if isinstance(x, (float, int, long)):
                v = CgfFormat.Vector3()
                v.x = self.x * x
                v.y = self.y * x
                v.z = self.z * x
                return v
            elif isinstance(x, CgfFormat.Vector3):
                return self.x * x.x + self.y * x.y + self.z * x.z
            elif isinstance(x, CgfFormat.Matrix33):
                v = CgfFormat.Vector3()
                v.x = self.x * x.m11 + self.y * x.m21 + self.z * x.m31
                v.y = self.x * x.m12 + self.y * x.m22 + self.z * x.m32
                v.z = self.x * x.m13 + self.y * x.m23 + self.z * x.m33
                return v
            elif isinstance(x, CgfFormat.Matrix44):
                return self * x.getMatrix33() + x.getTranslation()
            else:
                raise TypeError("do not know how to multiply Vector3 with %s"%x.__class__)

        def __rmul__(self, x):
            if isinstance(x, (float, int, long)):
                v = CgfFormat.Vector3()
                v.x = x * self.x
                v.y = x * self.y
                v.z = x * self.z
                return v
            else:
                raise TypeError("do not know how to multiply %s and Vector3"%x.__class__)

        def __div__(self, x):
            if isinstance(x, (float, int, long)):
                v = CgfFormat.Vector3()
                v.x = self.x / x
                v.y = self.y / x
                v.z = self.z / x
                return v
            else:
                raise TypeError("do not know how to divide Vector3 and %s"%x.__class__)

        def __add__(self, x):
            if isinstance(x, (float, int, long)):
                v = CgfFormat.Vector3()
                v.x = self.x + x
                v.y = self.y + x
                v.z = self.z + x
                return v
            elif isinstance(x, CgfFormat.Vector3):
                v = CgfFormat.Vector3()
                v.x = self.x + x.x
                v.y = self.y + x.y
                v.z = self.z + x.z
                return v
            else:
                raise TypeError("do not know how to add Vector3 and %s"%x.__class__)

        def __radd__(self, x):
            if isinstance(x, (float, int, long)):
                v = CgfFormat.Vector3()
                v.x = x + self.x
                v.y = x + self.y
                v.z = x + self.z
                return v
            else:
                raise TypeError("do not know how to add %s and Vector3"%x.__class__)

        def __sub__(self, x):
            if isinstance(x, (float, int, long)):
                v = CgfFormat.Vector3()
                v.x = self.x - x
                v.y = self.y - x
                v.z = self.z - x
                return v
            elif isinstance(x, CgfFormat.Vector3):
                v = CgfFormat.Vector3()
                v.x = self.x - x.x
                v.y = self.y - x.y
                v.z = self.z - x.z
                return v
            else:
                raise TypeError("do not know how to substract Vector3 and %s"%x.__class__)

        def __rsub__(self, x):
            if isinstance(x, (float, int, long)):
                v = CgfFormat.Vector3()
                v.x = x - self.x
                v.y = x - self.y
                v.z = x - self.z
                return v
            else:
                raise TypeError("do not know how to substract %s and Vector3"%x.__class__)

        def __neg__(self):
            v = CgfFormat.Vector3()
            v.x = -self.x
            v.y = -self.y
            v.z = -self.z
            return v

        # cross product
        def crossproduct(self, x):
            if isinstance(x, CgfFormat.Vector3):
                v = CgfFormat.Vector3()
                v.x = self.y*x.z - self.z*x.y
                v.y = self.z*x.x - self.x*x.z
                v.z = self.x*x.y - self.y*x.x
                return v
            else:
                raise TypeError("do not know how to calculate crossproduct of Vector3 and %s"%x.__class__)

        def __eq__(self, x):
            if isinstance(x, type(None)):
                return False
            if not isinstance(x, CgfFormat.Vector3):
                raise TypeError("do not know how to compare Vector3 and %s"%x.__class__)
            if abs(self.x - x.x) > CgfFormat.EPSILON: return False
            if abs(self.y - x.y) > CgfFormat.EPSILON: return False
            if abs(self.z - x.z) > CgfFormat.EPSILON: return False
            return True

        def __ne__(self, x):
            return not self.__eq__(x)
