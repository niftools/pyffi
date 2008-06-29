"""
This module implements the CGF file format.

Examples
========

Read a CGF file
---------------

>>> # get file version and file type, and read cgf file
>>> stream = open('tests/cgf/test.cgf', 'rb')
>>> version, user_version = CgfFormat.getVersion(stream)
>>> if version == -1:
...     raise RuntimeError('cgf version not supported')
... elif version == -2:
...     raise RuntimeError('not a cgf file')
>>> filetype, chunks, versions = CgfFormat.read(stream,
...                                             version = version,
...                                             user_version = user_version)
>>> # print all chunks
>>> for chunk in chunks:
...     print chunk # doctest: +ELLIPSIS
<class 'PyFFI.XmlHandler.SourceInfoChunk'> instance at ...
* sourceFile : <EMPTY STRING>
* date : Fri Sep 28 22:40:44 2007
* author : blender@BLENDER
<BLANKLINE>
<class 'PyFFI.XmlHandler.TimingChunk'> instance at ...
* secsPerTick : 0.000208333338378
* ticksPerFrame : 160
* globalRange :
    <class 'PyFFI.XmlHandler.RangeEntity'> instance at ...
    * name : GlobalRange
    * start : 0
    * end : 100
* numSubRanges : 0
<BLANKLINE>

Parse all CGF files in a directory tree
---------------------------------------

>>> for filetype, chunks, versions in CgfFormat.walk('tests/cgf',
...                                                  raisereaderror = False,
...                                                  verbose = 1):
...     pass
reading tests/cgf/test.cgf

Create a CGF file from scratch
------------------------------

>>> from PyFFI.Formats.CGF import CgfFormat
>>> node1 = CgfFormat.NodeChunk()
>>> node1.name = "hello"
>>> node2 = CgfFormat.NodeChunk()
>>> node1.numChildren = 1
>>> node1.children.updateSize()
>>> node1.children[0] = node2
>>> node2.name = "world"
>>> chunks = [node1, node2]
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> # note: write returns number of padding bytes
>>> CgfFormat.write(
...     stream,
...     version = CgfFormat.VER_FARCRY,
...     user_version = CgfFormat.UVER_FARCRY,
...     filetype = CgfFormat.FileType.GEOM,
...     chunks = chunks)
0
>>> stream.seek(0)
>>> version, user_version = CgfFormat.getVersion(stream)
>>> if version == -1:
...     raise RuntimeError('cgf version not supported')
... elif version == -2:
...     raise RuntimeError('not a cgf file')
>>> filetype, chunks, versions = CgfFormat.read(stream,
...                                             version = version,
...                                             user_version = user_version)
>>> # print all chunks
>>> for chunk in chunks:
...     print chunk # doctest: +ELLIPSIS
<class 'PyFFI.XmlHandler.NodeChunk'> instance at 0x...
* name : hello
* object : None
* parent : None
* numChildren : 1
* material : None
* isGroupHead : False
* isGroupMember : False
* reserved1 :
    <class 'PyFFI.Bases.Array.Array'> instance at 0x...
    0: 0
    1: 0
* transform :
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
* pos : [  0.000  0.000  0.000 ]
* rot :
    <class 'PyFFI.XmlHandler.Quat'> instance at 0x...
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
    <class 'PyFFI.Bases.Array.Array'> instance at 0x...
    0: <class 'PyFFI.XmlHandler.NodeChunk'> instance at 0x...
<BLANKLINE>
<class 'PyFFI.XmlHandler.NodeChunk'> instance at 0x...
* name : world
* object : None
* parent : None
* numChildren : 0
* material : None
* isGroupHead : False
* isGroupMember : False
* reserved1 :
    <class 'PyFFI.Bases.Array.Array'> instance at 0x...
    0: 0
    1: 0
* transform :
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
* pos : [  0.000  0.000  0.000 ]
* rot :
    <class 'PyFFI.XmlHandler.Quat'> instance at 0x...
    * x : 0.0
    * y : 0.0
    * z : 0.0
    * w : 0.0
* scl : [  0.000  0.000  0.000 ]
* posCtrl : None
* rotCtrl : None
* sclCtrl : None
* propertyString : <EMPTY STRING>
* children : <class 'PyFFI.Bases.Array.Array'> instance at 0x...
<BLANKLINE>
"""

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

import struct, os, re

from types import NoneType

from PyFFI import XmlFileFormat
from PyFFI import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI import Common
from PyFFI.Bases.Basic import BasicBase

class CgfFormat(XmlFileFormat):
    """Stores all information about the cgf file format."""
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'cgf.xml'
    # where to look for cgf.xml and in what order: CGFXMLPATH env var,
    # or module directory
    xmlFilePath = [os.getenv('CGFXMLPATH'), os.path.dirname(__file__)]
    clsFilePath = os.path.dirname(__file__) # path of class customizers
    EPSILON = 0.0001 # used for comparing floats
    # regular expression for file name extension matching on cgf files
    re_filename = re.compile(r'^.*\.(cgf|cga|chr|caf)$', re.IGNORECASE)

    # version and user version for far cry
    VER_FARCRY = 0x744
    UVER_FARCRY = 1

    # version and user version for crysis
    VER_CRYSIS = 0x744
    UVER_CRYSIS = 2

    # basic types
    int = Common.Int
    uint = Common.UInt
    byte = Common.Byte
    ubyte = Common.UByte
    short = Common.Short
    ushort = Common.UShort
    char = Common.Char
    float = Common.Float
    bool = Common.Bool
    String = Common.ZString
    SizedString = Common.SizedString

    class String16(Common.FixedString):
        """String of fixed length 16."""
        _len = 16

    class String32(Common.FixedString):
        """String of fixed length 32."""
        _len = 32

    class String64(Common.FixedString):
        """String of fixed length 64."""
        _len = 64

    class String128(Common.FixedString):
        """String of fixed length 128."""
        _len = 128

    class String256(Common.FixedString):
        """String of fixed length 256."""
        _len = 256

    class FileSignature(BasicBase):
        """The CryTek file signature 'CryTex\x00\x00' with which every
        cgf file starts."""
        def __init__(self, **kwargs):
            super(CgfFormat.FileSignature, self).__init__(**kwargs)

        def __str__(self):
            return 'CryTek\x00\x00'

        def read(self, stream, **kwargs):
            """Read signature from stream.

            @param stream: The stream to read from.
            @type stream: file
            """
            signat = stream.read(8)
            if signat[:6] != self.__str__()[:6]:
                raise ValueError(
                    "invalid CGF signature: expected '%s' but got '%s'"
                    %(self.__str__(), signat))

        def write(self, stream, **kwargs):
            """Write signature to stream.

            @param stream: The stream to read from.
            @type stream: file
            """
            stream.write(self.__str__())

        def getValue(self):
            """Get signature.

            @return: The signature.
            """
            return self.__str__()

        def setValue(self, value):
            """Set signature.

            @param value: The value to assign (should be 'Crytek\\x00\\x00').
            @type value: str
            """
            if value != self.__str__():
                raise ValueError(
                    "invalid CGF signature: expected '%s' but got '%s'"
                    %(self.__str__(), value))

        def getSize(self, **kwargs):
            """Return number of bytes that the signature occupies in a file.

            @return: Number of bytes.
            """
            return 8

        def getHash(self, **kwargs):
            """Return a hash value for the signature.

            @return: An immutable object that can be used as a hash.
            """
            return self.__str__()

    class Ref(BasicBase):
        """Reference to a chunk, up the hierarchy."""
        _isTemplate = True
        _hasLinks = True
        _hasRefs = True
        def __init__(self, **kwargs):
            super(CgfFormat.Ref, self).__init__(**kwargs)
            self._template = kwargs.get('template', NoneType)
            self._value = None

        def getValue(self):
            """Get chunk being referred to.

            @return: The chunk being referred to.
            """
            return self._value

        def setValue(self, value):
            """Set chunk reference.

            @param value: The value to assign.
            @type value: L{CgfFormat.Chunk}
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

            @param stream: The stream to read from.
            @type stream: file
            @param link_stack: The stack containing all block indices.
            @type link_stack: list of ints
            """
            self._value = None # fixLinks will set this field
            block_index, = struct.unpack('<i', stream.read(4))
            kwargs.get('link_stack', []).append(block_index)

        def write(self, stream, **kwargs):
            """Write chunk index.

            @param stream: The stream to write to.
            @type stream: file
            @param block_index_dct: Dictionary mapping blocks to indices.
            @type block_index_dct: dict
            """
            if self._value == None:
                stream.write('\xff\xff\xff\xff')
            else:
                stream.write(struct.pack(
                    '<i', kwargs.get('block_index_dct')[self._value]))

        def fixLinks(self, **kwargs):
            """Resolve chunk index into a chunk.

            @param block_dct: Dictionary mapping block index to block.
            @type block_dct: dict
            @param link_stack: The stack containing all block indices.
            @type link_stack: list of ints
            """

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
                print("WARNING: invalid chunk reference (%i)" % block_index)
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
                    print("""\
WARNING: expected instance of %s
         but got instance of %s""" % (self._template, block.__class__))
            self._value = block

        def getLinks(self, **kwargs):
            """Return the chunk reference.

            @return: Empty list if no reference, or single item list containing
                the reference.
            """
            if self._value != None:
                return [self._value]
            else:
                return []

        def getRefs(self, **kwargs):
            """Return the chunk reference.

            @return: Empty list if no reference, or single item list containing
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

            @return: Number of bytes.
            """
            return 4

        def getHash(self, **kwargs):
            """Return a hash value for the chunk referred to.

            @return: An immutable object that can be used as a hash.
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

            @return: C{[]}
            """
            return []

    # exceptions
    class CgfError(StandardError):
        """Exception for CGF specific errors."""
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        @param version_str: The version string.
        @type version_str: str
        @return: A version integer.

        >>> hex(CgfFormat.versionNumber('744'))
        '0x744'
        """
        return int(version_str, 16)

    @classmethod
    def getVersion(cls, stream):
        """Returns version of the chunk table, and game as user_version.
        Far Cry is user_version L{CgfFormat.UVER_FARCRY} and Crysis is
        user_version L{CgfFormat.UVER_CRYSIS}. Preserves the stream position.

        @param stream: The stream from which to read.
        @type stream: file
        @return: A pair (version, user_version).
            The returned version is -1 if the file type or chunk table version
            is not supported, and -2 if the file is not a cgf file.
        """
        pos = stream.tell()
        try:
            signat = stream.read(8)
            filetype, version, offset = struct.unpack('<III',
                                                      stream.read(12))
        except StandardError:
            return -2, 0
        finally:
            stream.seek(pos)
        if signat[:6] != "CryTek":
            return -2, 0
        if filetype not in [cls.FileType.GEOM, cls.FileType.ANIM]:
            return -1, 0
        if version not in cls.versions.values():
            return -1, 0
        # quick and lame game check:
        # far cry has chunk table at the end, crysis at the start
        if offset == 0x14:
            return version, cls.UVER_CRYSIS
        else:
            return version, cls.UVER_FARCRY

    @classmethod
    def getGame(cls, version = None, user_version = None):
        """Guess game based on version and user_version. This is the inverse of
        L{getGameVersion}.

        @param version: The version as obtained by L{getVersion}.
        @type version: int
        @param user_version: The user version as obtained by L{getVersion}.
        @type user_version: int
        @return: 'Crysis' or 'Far Cry'
        """
        try:
            return {cls.UVER_FARCRY: "Far Cry",
                    cls.UVER_CRYSIS: "Crysis"}[user_version]
        except KeyError:
            raise ValueError("unknown version 0x%X and user version %i" %
                             (version, user_version))

    @classmethod
    def getGameVersion(cls, game = None):
        """Get version and user_version for a particular game. This is the
        inverse of L{getGame}.

        @param game: 'Crysis' or 'Far Cry'.
        @type game: str
        @return: The version and user version.

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

        @param stream: The stream from which to read.
        @type stream: file
        @param version: The version as obtained by L{getVersion}.
        @type version: int
        @param user_version: The user version as obtained by L{getVersion}.
        @type user_version: int
        @return: L{FileType.GEOM} or L{FileType.ANIM}
        """
        pos = stream.tell()
        try:
            signat = stream.read(8)
            filetype, = struct.unpack('<I',
                                      stream.read(4))
        finally:
            stream.seek(pos)
        return filetype

    @classmethod
    def read(cls, stream, version = None, user_version = None,
             verbose = 0, validate = True):
        """Read cgf from stream.

        @param stream: The stream from which to read.
        @type stream: file
        @param version: The version as obtained by L{getVersion}.
        @type version: int
        @param user_version: The user version as obtained by L{getVersion}.
        @type user_version: int
        @param verbose: The level of verbosity.
        @type verbose: int
        @param validate: If C{True} then the chunk size as read is compared to
            the chunk size as expected. If there is a mismatch, then a warning
            will be printed.
        @type validate: bool
        @return: (filetype as int, chunks as list of L{CgfFormat.Chunk}s,
            versions as list of ints)
        """

        # game string
        game = cls.getGame(version = version, user_version = user_version)

        #print version, user_version, game # DEBUG

        # is it a caf file? these are missing chunk headers on controllers
        is_caf = (stream.name[-4:].lower() == ".caf")

        chunk_types = [
            chunk_type for chunk_type in dir(cls.ChunkType) \
            if chunk_type[:2] != '__']

        # read header
        hdr = cls.Header()
        hdr.read(stream, version = version, user_version = user_version)

        # read chunk table
        stream.seek(hdr.offset)
        table = cls.ChunkTable()
        table.read(stream, version = version, user_version = user_version)

        # get the chunk sizes (for double checking that we have all data)
        if validate:
            chunk_offsets = [chunkhdr.offset for chunkhdr in table.chunkHeaders]
            chunk_offsets.append(hdr.offset)
            chunk_sizes = []
            for chunkhdr in table.chunkHeaders:
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
        chunks = [] # records all chunks as read from cgf file in proper order
        versions = [] # records all chunk versions as read from cgf file
        for chunknum, chunkhdr in enumerate(table.chunkHeaders):
            # check that id is unique
            if chunkhdr.id in chunk_dct:
                raise ValueError('chunk id %i not unique'%chunkhdr.id)

            # get chunk type
            for chunk_type in chunk_types:
                if getattr(cls.ChunkType, chunk_type) == chunkhdr.type:
                    break
            else:
                raise ValueError('unknown chunk type 0x%08X'%chunkhdr.type)
            #print "%s chunk, version 0x%08X" % (chunk_type, chunkhdr.version)
            try:
                chunk = getattr(cls, '%sChunk' % chunk_type)()
            except AttributeError:
                raise ValueError(
                    'undecoded chunk type 0x%08X (%sChunk)'
                    %(chunkhdr.type, chunk_type))
            # check the chunk version
            if not game in chunk.getGames():
                raise ValueError(
                    'game %s does not support %sChunk'
                    % (game, chunk_type))
            if not chunkhdr.version in chunk.getVersions(game):
                raise ValueError(
                    'chunk version 0x%08X not supported for game %s and %sChunk'
                    % (chunkhdr.version, game, chunk_type))

            # now read the chunk
            stream.seek(chunkhdr.offset)

            # in far cry, most chunks start with a copy of chunkhdr
            # in crysis, more chunks start with chunkhdr
            # caf files are special: they don't have headers on controllers
            if not(user_version == cls.UVER_FARCRY
                   and chunkhdr.type in [
                       cls.ChunkType.SourceInfo,
                       cls.ChunkType.BoneNameList,
                       cls.ChunkType.BoneLightBinding,
                       cls.ChunkType.BoneInitialPos,
                       cls.ChunkType.MeshMorphTarget]) \
                and not(user_version == cls.UVER_CRYSIS
                        and chunkhdr.type in [
                            cls.ChunkType.BoneNameList,
                            cls.ChunkType.BoneInitialPos]) \
                and not(is_caf
                        and chunkhdr.type in [
                            cls.ChunkType.Controller]):
                chunkhdr_copy = cls.ChunkHeader()
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
            chunks.append(chunk)
            versions.append(chunkhdr.version)
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
                    print("""\
BUG: getSize returns wrong size when reading %s at 0x%08X
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
                    print("""\
WARNING: chunk size mismatch when reading %s at 0x%08X
         %i bytes available, but actual bytes read is %i"""
                          % (chunk.__class__.__name__,
                             chunkhdr.offset,
                             chunk_sizes[chunknum], size))

        # fix links
        for chunk, chunkversion in zip(chunks, versions):
            #print chunk.__class__
            chunk.fixLinks(
                version = chunkversion, user_version = user_version,
                block_dct = chunk_dct, link_stack = link_stack)
        if link_stack != []:
            raise cls.CgfError(
                'not all links have been popped from the stack (bug?)')

        return hdr.type, chunks, versions

    @classmethod
    def write(cls, stream, version = None, user_version = None,
              filetype = None, chunks = None, versions = None,
              verbose = 0):
        """Write cgf to stream. Returns number of padding bytes written.

        @param stream: The stream to which to write.
        @type stream: file
        @param version: The version number.
        @type version: int
        @param user_version: The user version number.
        @type user_version: int
        @param filetype: The file type, L{FileType.GEOM} or L{FileType.ANIM}.
        @type filetype: int
        @param chunks: The file chunks.
        @type chunks: list of L{CgfFormat.Chunk}s
        @param versions: The file chunk versions. If C{None} then these will
            be automatically obtained through L{getChunkVersions}.
        @type versions: list of ints
        @param verbose: The level of verbosity.
        @type verbose: int
        @return: Number of padding bytes written.
        """

        # DEBUG
        #print((stream, version, user_version, filetype, chunks, versions))

        # game string
        game = cls.getGame(version = version, user_version = user_version)
        #print(game) # DEBUG

        # is it a caf file? these are missing chunk headers on controllers
        is_caf = (stream.name[-4:].lower() == ".caf")

        # variable to track number of padding bytes
        total_padding = 0

        # chunk versions
        if versions is None:
            versions = cls.getChunkVersions(version = version,
                                            user_version = user_version,
                                            chunks = chunks)

        # write header
        hdr_pos = stream.tell()
        hdr = cls.Header()
        hdr.type = filetype
        hdr.version = version
        hdr.offset = -1 # is set at the end
        hdr.write(stream, version = version, user_version = user_version)

        # chunk id is simply its index in the chunks list
        block_index_dct = dict((chunk, i) for i, chunk in enumerate(chunks))

        # write chunks and add headers to chunk table
        table = cls.ChunkTable()
        table.numChunks = len(chunks)
        table.chunkHeaders.updateSize()
        #print(table) # DEBUG

        # crysis: write chunk table now
        if user_version == cls.UVER_CRYSIS:
            hdr.offset = stream.tell()
            table.write(stream,
                        version = version, user_version = user_version)

        for chunkhdr, chunk, chunkversion in zip(table.chunkHeaders,
                                                 chunks, versions):
            # set up chunk header
            chunkhdr.type = getattr(
                cls.ChunkType, chunk.__class__.__name__[:-5])
            chunkhdr.version = chunkversion
            chunkhdr.offset = stream.tell()
            chunkhdr.id = block_index_dct[chunk]
            # write chunk header
            if not(user_version == cls.UVER_FARCRY
                   and chunkhdr.type in [
                       cls.ChunkType.SourceInfo,
                       cls.ChunkType.BoneNameList,
                       cls.ChunkType.BoneLightBinding,
                       cls.ChunkType.BoneInitialPos,
                       cls.ChunkType.MeshMorphTarget]) \
                and not(user_version == cls.UVER_CRYSIS
                        and chunkhdr.type in [
                            cls.ChunkType.BoneNameList,
                            cls.ChunkType.BoneInitialPos]) \
                and not(is_caf
                        and chunkhdr.type in [
                            cls.ChunkType.Controller]):
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
        if user_version == cls.UVER_CRYSIS:
            end_pos = stream.tell()
            stream.seek(hdr.offset)
            table.write(stream, version = version, user_version = user_version)
        else:
            hdr.offset = stream.tell()
            table.write(stream, version = version, user_version = user_version)
            end_pos = stream.tell()

        # update header
        stream.seek(hdr_pos)
        hdr.write(stream, version = version, user_version = user_version)

        # seek end of written data
        stream.seek(end_pos)

        # return number of padding bytes written
        return total_padding

    @classmethod
    def getChunkVersions(cls, version = None, user_version = None,
                         chunks = None):
        """Return version of each chunk in the chunk list for the
        given file version and file user version.

        @param version: The version.
        @type version: int
        @param user_version: The user version.
        @type user_version: int
        @param chunks: List of chunks.
        @type chunks: list of L{CgfFormat.Chunk}
        @return: Version of each chunk as list of ints (same length as
            C{chunks}).
        """

        # game string
        game = cls.getGame(version = version, user_version = user_version)

        try:
            return [max(chunk.getVersions(game)) for chunk in chunks]
        except KeyError:
            raise cls.CgfError("game %s not supported" % game)
