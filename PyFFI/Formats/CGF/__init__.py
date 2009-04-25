"""
.. :mod:`PyFFI.Formats.CGF` --- Crytek (.cgf and .cga)
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
<class 'PyFFI.ObjectModels.XML.FileFormat.SourceInfoChunk'> instance at ...
* sourceFile : <EMPTY STRING>
* date : Fri Sep 28 22:40:44 2007
* author : blender@BLENDER
<BLANKLINE>
<class 'PyFFI.ObjectModels.XML.FileFormat.TimingChunk'> instance at ...
* secsPerTick : 0.000208333338378
* ticksPerFrame : 160
* globalRange :
    <class 'PyFFI.ObjectModels.XML.FileFormat.RangeEntity'> instance at ...
    * name : GlobalRange
    * start : 0
    * end : 100
* numSubRanges : 0
<BLANKLINE>

Parse all CGF files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in CgfFormat.walkData('tests/cgf'):
...     print stream.name
tests/cgf/invalid.cgf
tests/cgf/monkey.cgf
tests/cgf/test.cgf
tests/cgf/vcols.cgf

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
...     print(chunk) # doctest: +ELLIPSIS
<class 'PyFFI.ObjectModels.XML.FileFormat.NodeChunk'> instance at 0x...
* name : hello
* object : None
* parent : None
* numChildren : 1
* material : None
* isGroupHead : False
* isGroupMember : False
* reserved1 :
    <class 'PyFFI.ObjectModels.XML.Array.Array'> instance at 0x...
    0: 0
    1: 0
* transform :
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
* pos : [  0.000  0.000  0.000 ]
* rot :
    <class 'PyFFI.ObjectModels.XML.FileFormat.Quat'> instance at 0x...
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
    <class 'PyFFI.ObjectModels.XML.Array.Array'> instance at 0x...
    0: <class 'PyFFI.ObjectModels.XML.FileFormat.NodeChunk'> instance at 0x...
<BLANKLINE>
<class 'PyFFI.ObjectModels.XML.FileFormat.NodeChunk'> instance at 0x...
* name : world
* object : None
* parent : None
* numChildren : 0
* material : None
* isGroupHead : False
* isGroupMember : False
* reserved1 :
    <class 'PyFFI.ObjectModels.XML.Array.Array'> instance at 0x...
    0: 0
    1: 0
* transform :
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
    [  0.000  0.000  0.000  0.000 ]
* pos : [  0.000  0.000  0.000 ]
* rot :
    <class 'PyFFI.ObjectModels.XML.FileFormat.Quat'> instance at 0x...
    * x : 0.0
    * y : 0.0
    * z : 0.0
    * w : 0.0
* scl : [  0.000  0.000  0.000 ]
* posCtrl : None
* rotCtrl : None
* sclCtrl : None
* propertyString : <EMPTY STRING>
* children : <class 'PyFFI.ObjectModels.XML.Array.Array'> instance at 0x...
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

import logging
import struct
import os
import re
import warnings

import PyFFI.ObjectModels.XML.FileFormat
from PyFFI import Utils
from PyFFI.ObjectModels import Common
from PyFFI.ObjectModels.XML.Basic import BasicBase
import PyFFI.ObjectModels.FileFormat
from PyFFI.ObjectModels.Graph import EdgeFilter

class CgfFormat(PyFFI.ObjectModels.XML.FileFormat.XmlFileFormat):
    """Stores all information about the cgf file format."""
    xmlFileName = 'cgf.xml'
    # where to look for cgf.xml and in what order: CGFXMLPATH env var,
    # or module directory
    xmlFilePath = [os.getenv('CGFXMLPATH'), os.path.dirname(__file__)]
    clsFilePath = os.path.dirname(__file__) # path of class customizers
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

    class Data(PyFFI.ObjectModels.FileFormat.FileFormat.Data):
        """A class to contain the actual nif data.

        Note that L{versions} and L{chunk_table} are not automatically kept
        in sync with the L{chunks}, but they are
        resynchronized when calling L{write}.

        :ivar game: The cgf game.
        :type game: C{int}
        :ivar header: The nif header.
        :type header: L{CgfFormat.Header}
        :ivar chunks: List of chunks (the actual data).
        :type chunks: C{list} of L{CgfFormat.Chunk}
        :ivar versions: List of chunk versions.
        :type versions: C{list} of L{int}
        """

        class VersionUInt(Common.UInt):
            def setValue(self, value):
                if value is None:
                    self._value = None
                else:
                    Common.UInt.setValue(self, value)

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
            :type filetype: C{int}
            :param game: The game.
            :type game: C{str}
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
            # map chunk type integers to chunk type classes
            # XXX should be a CgfFormat class variable... this hack is nasty
            # XXX move to class level when inheritance is implemented
            CgfFormat.CHUNK_MAP = dict(
                (getattr(CgfFormat.ChunkType, chunk_name),
                 getattr(CgfFormat, '%sChunk' % chunk_name))
                for chunk_name in CgfFormat.ChunkType._enumkeys
                if chunk_name != "ANY")

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
            :type stream: C{file}
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

        # overriding PyFFI.ObjectModels.FileFormat.FileFormat.Data methods

        def inspect(self, stream):
            """Quickly checks whether the stream appears to contain
            cgf data, and read the cgf header and chunk table. Resets stream to
            original position.

            Call this function if you only need to inspect the header and
            chunk table.

            :param stream: The file to inspect.
            :type stream: C{file}
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
            :type stream: C{file}
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

    # implementation of cgf-specific basic types

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

    # exceptions
    class CgfError(StandardError):
        """Exception for CGF specific errors."""
        pass

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
        """Returns list of all root blocks. Used by L{PyFFI.QSkope}
        and L{PyFFI.Spells}.

        :param readresult: Result from L{walk} or L{read}.
        :type readresult: tuple
        :return: list of root blocks
        @deprecated: This function simply returns an empty list, and will eventually be removed.
        """
        warnings.warn("do not use the getRoots function", DeprecationWarning)
        return []

    @classmethod
    def getBlocks(cls, *readresult):
        """Returns list of all blocks. Used by L{PyFFI.QSkope}
        and L{PyFFI.Spells}.

        :param readresult: Result from L{walk} or L{read}.
        :type readresult: tuple
        :return: list of blocks
        @deprecated: Use L{Data.chunks} instead.
        """
        warnings.warn("use CgfFormat.Data.chunks", DeprecationWarning)
        return readresult[1]
