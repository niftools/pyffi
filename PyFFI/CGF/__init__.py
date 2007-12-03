"""
This module implements the CGF file format.

Examples
========

Read a CGF file
---------------
>>> # get file version and file type, and read cgf file
>>> stream = open('test.cgf', 'rb')
>>> filetype, fileversion = CgfFormat.getVersion(stream)
>>> if filetype == -1:
...     raise RuntimeError('cgf version not supported')
... elif filetype == -2:
...     raise RuntimeError('not a cgf file')
>>> chunks, versions = CgfFormat.read(stream, fileversion = fileversion)
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
"""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, Python File Format Interface
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

from PyFFI import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI import Common
from PyFFI.Bases.Basic import BasicBase

class CgfFormat(object):
    """Stores all information about the cgf file format."""
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'cgf.xml'
    # where to look for cgf.xml and in what order: CGFXMLPATH env var,
    # or module directory
    xmlFilePath = [ os.getenv('CGFXMLPATH'), os.path.dirname(__file__) ]
    clsFilePath = os.path.dirname(__file__) # path of class customizers
    EPSILON = 0.0001 # used for comparing floats
    
    # basic types
    int = Common.Int
    uint = Common.UInt
    byte = Common.Byte
    ubyte = Common.UByte
    short = Common.Short
    ushort = Common.UShort
    char = Common.Char
    float = Common.Float

    class FileSignature(BasicBase):
        """The CryTek file signature 'CryTex\x00\x00' with which every
        cgf file starts."""
        def __init__(self, **kwargs):
            super(CgfFormat.FileSignature, self).__init__(**kwargs)

        def __str__(self):
            return 'CryTek\x00\x00'

        def read(self, stream, **kwargs):
            """Read signature from stream."""
            signat = stream.read(8)
            if signat[:6] != self.__str__()[:6]:
                raise ValueError(
                    "invalid CGF signature: expected '%s' but got '%s'"
                    %(self.__str__(), signat))

        def write(self, stream, **kwargs):
            """Write signature to stream."""
            stream.write(self.__str__())

        def getValue(self):
            """Get signature."""
            return self.__str__()

        def setValue(self, value):
            """Set signature."""
            if value != self.__str__():
                raise ValueError(
                    "invalid CGF signature: expected '%s' but got '%s'"
                    %(self.__str__(), value))

        def getSize(self, **kwargs):
            """Get signature size in bytes."""
            return 8

        def getHash(self, **kwargs):
            """Get signature hash value."""
            return self.__str__()

    class String(BasicBase):
        """String of variable length (null terminated)."""
        def __init__(self, **kwargs):
            super(CgfFormat.String, self).__init__(**kwargs)
            self._value = ""

        def __str__(self):
            if not self._value:
                return '<EMPTY STRING>'
            return self._value

        def getValue(self):
            """Return the string."""
            return self._value

        def setValue(self, value):
            """Set the string."""
            val = str(value)
            i = val.find('\x00')
            if i != -1:
                val = val[:i]
            self._value = val

        def read(self, stream, **kwargs):
            """Read string from stream."""
            i = 0
            self._value = ''
            char = ''
            while char != '\x00':
                i += 1
                if i > 1000:
                    raise ValueError('string too long')
                self._value += char
                char = stream.read(1)

        def write(self, stream, **kwargs):
            """Write string to stream."""
            stream.write(self._value)
            stream.write('\x00')

        def getSize(self, **kwargs):
            """Return string size in bytes."""
            return len(self._value) + 1

        def getHash(self, **kwargs):
            """Return hash value for the string."""
            return self._value

    class String32(BasicBase):
        """String of fixed length 32."""
        _len = 32
        
        def __init__(self, **kwargs):
            super(CgfFormat.String32, self).__init__(**kwargs)
            self._value = ""

        def __str__(self):
            if not self._value:
                return '<EMPTY STRING>'
            return self._value

        def getValue(self):
            """Return the string."""
            return self._value

        def setValue(self, value):
            """Set the string."""
            val = str(value)
            if len(val) > self._len:
                raise ValueError("string '%s' too long" % val)
            self._value = val

        def read(self, stream, **kwargs):
            """Read string from stream."""
            self._value = stream.read(self._len)
            i = self._value.find('\x00')
            if i != -1:
                self._value = self._value[:i]

        def write(self, stream, **kwargs):
            """Write string to stream."""
            stream.write(self._value.ljust(self._len, "\x00"))

        def getSize(self, **kwargs):
            """Return string size in bytes."""
            return self._len

        def getHash(self, **kwargs):
            """Return hash value for the string."""
            return self._value

    class String64(String32):
        """String of fixed length 64."""
        _len = 64

    class String128(String32):
        """String of fixed length 128."""
        _len = 128

    class String256(String32):
        """String of fixed length 256."""
        _len = 256

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
            """Get chunk being referred to."""
            return self._value

        def setValue(self, value):
            """Set chunk reference."""
            if value == None:
                self._value = None
            else:
                if not isinstance(value, self._template):
                    raise TypeError(
                        'expected an instance of %s but got instance of %s'
                        %(self._template, value.__class__))
                self._value = value

        def read(self, stream, **kwargs):
            """Read chunk index."""
            self._value = None # fixLinks will set this field
            block_index, = struct.unpack('<i', stream.read(4))
            kwargs.get('link_stack', []).append(block_index)

        def write(self, stream, **kwargs):
            """Write chunk index."""
            if self._value == None:
                stream.write('\xff\xff\xff\xff')
            else:
                stream.write(struct.pack(
                    '<i', kwargs.get('block_index_dct')[self._value]))

        def fixLinks(self, **kwargs):
            """Resolve chunk index into a chunk."""
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
                print "WARNING: invalid chunk reference (%i)" % block_index
                self._value = None
                return
            if not isinstance(block, self._template):
                # make this raise an exception when all reference errors
                # are sorted out
                print('WARNING: expected instance of %s but got instance of %s'
                      %(self._template, block.__class__))
            self._value = block

        def getLinks(self, **kwargs):
            """Return the chunk reference."""
            if self._value != None:
                return [self._value]
            else:
                return []

        def getRefs(self, **kwargs):
            """Return the chunk reference."""
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
            """Return link size in bytes."""
            return 4

        def getHash(self, **kwargs):
            """Return hash of chunk referred to."""
            return self._value.getHash()if not self._value is None else None

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
            """Ptr does not point down, so getRefs returns empty list."""
            return []

    # exceptions
    class CgfError(StandardError):
        """Exception for CGF specific errors."""
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        >>> hex(CgfFormat.versionNumber('744'))
        '0x744'
        """
        return int(version_str, 16)

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable
        by Python.

        >>> CgfFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """

        # str(name) converts name to string in case name is a unicode string
        parts = str(name).split()
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    @classmethod
    def getVersion(cls, stream):
        """Returns file type (geometry or animation) and version of the
        chunk table.

        Returns -1, 0 if file type or chunk table version is not supported.
        Returns -2, 0 if it is not a cgf file.
        """
        pos = stream.tell()
        try:
            signat = stream.read(8)
            filetype, fileversion = struct.unpack('<II', stream.read(8))
        except StandardError:
            return -2, 0
        finally:
            stream.seek(pos)
        if signat[:6] != "CryTek":
            return -2, 0
        if filetype not in [ cls.FileType.GEOM, cls.FileType.ANIM ]:
            return -1, 0
        if fileversion not in cls.versions.values():
            return -1, 0
        return filetype, fileversion

    @classmethod
    def read(cls, stream, fileversion = None, verbose = 0):
        """Read cgf from stream."""
        chunk_types = [
            chunk_type for chunk_type in dir(cls.ChunkType) \
            if chunk_type[:2] != '__']

        # read header
        hdr = cls.Header()
        hdr.read(stream, version = fileversion)

        # read chunk table
        stream.seek(hdr.offset)
        table = cls.ChunkTable()
        table.read(stream, version = hdr.version)

        # read the chunks
        link_stack = [] # list of chunk identifiers, as added to the stack
        chunk_dct = {} # maps chunk index to actual chunk
        chunks = [] # records all chunks as read from cgf file in proper order
        versions = [] # records all chunk versions as read from cgf file
        for chunkhdr in table.chunkHeaders:
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

            # now read the chunk
            stream.seek(chunkhdr.offset)

            # most chunks start with a copy of chunkhdr
            if chunkhdr.type not in [
                cls.ChunkType.SourceInfo, cls.ChunkType.BoneNameList,
                cls.ChunkType.BoneLightBinding, cls.ChunkType.BoneInitialPos,
                cls.ChunkType.MeshMorphTarget]:
                
                chunkhdr_copy = cls.ChunkHeader()
                chunkhdr_copy.read(stream, version = hdr.version)
                # check that the copy is valid
                if chunkhdr_copy.type != chunkhdr.type \
                   or chunkhdr_copy.version != chunkhdr.version \
                   or chunkhdr_copy.offset != chunkhdr.offset \
                   or chunkhdr_copy.id != chunkhdr.id:
                    raise ValueError(
                        'chunk starts with invalid header:\n\
expected\n%sbut got\n%s'%(chunkhdr, chunkhdr_copy))

            chunk.read(
                stream, version = chunkhdr.version, link_stack = link_stack)
            chunks.append(chunk)
            versions.append(chunkhdr.version)
            chunk_dct[chunkhdr.id] = chunk

        # fix links
        for chunk, version in zip(chunks, versions):
            #print chunk.__class__
            chunk.fixLinks(
                version = version,
                block_dct = chunk_dct, link_stack = link_stack)
        if link_stack != []:
            raise cls.CgfError(
                'not all links have been popped from the stack (bug?)')

        return chunks, versions

    @classmethod
    def write(cls,
              stream,
              filetype = None, fileversion = None,
              chunks = None, versions = None, verbose = 0):
        """Write cgf to stream."""
        # write header
        hdr_pos = stream.tell()
        hdr = cls.Header()
        hdr.type = filetype
        hdr.version = fileversion
        hdr.offset = -1 # is set at the end
        hdr.write(stream, version = fileversion)

        # chunk id is simply its index in the chunks list
        block_index_dct = dict((chunk, i) for i, chunk in enumerate(chunks))

        # write chunks and add headers to chunk table
        table = cls.ChunkTable()
        table.numChunks = len(chunks)
        table.chunkHeaders.updateSize()
        for chunkhdr, chunk, version in zip(table.chunkHeaders,
                                            chunks, versions):
            chunkhdr.type = getattr(
                cls.ChunkType, chunk.__class__.__name__[:-5])
            chunkhdr.version = version
            chunkhdr.offset = stream.tell()
            chunkhdr.id = block_index_dct[chunk]
            # write chunk header
            if chunkhdr.type not in [
                cls.ChunkType.SourceInfo, cls.ChunkType.BoneNameList,
                cls.ChunkType.BoneLightBinding, cls.ChunkType.BoneInitialPos,
                cls.ChunkType.MeshMorphTarget]:
                chunkhdr.write(stream, version = fileversion)
            # write chunk
            chunk.write(
                stream, version = version, block_index_dct = block_index_dct)

        # write chunk table
        hdr.offset = stream.tell()
        table.write(stream, version = fileversion)

        # update header
        stream.seek(hdr_pos)
        hdr.write(stream, version = fileversion)

    @classmethod
    def getFileVersion(cls, game = 'FarCry'):
        """Return file version for C{game}."""
        if game == 'FarCry':
            return 0x744
        else:
            raise cls.CgfError("game %s not supported"%game)

    @classmethod
    def getChunkVersions(cls, game = 'FarCry', chunks = None):
        """Return version list that matches the chunk list C{chunks} for the
        given C{game}."""
        if game == 'FarCry':
            version_dct = dict([
                (cls.MtlChunk, 0x746),
                (cls.NodeChunk, 0x823),
                (cls.TimingChunk, 0x918),
                (cls.SourceInfoChunk, 0x000),
                (cls.MeshChunk, 0x744),
                (cls.ControllerChunk, 0x827),
                (cls.BoneAnimChunk, 0x290),
                (cls.BoneNameListChunk, 0x745),
                (cls.MeshMorphTargetChunk, 0x001),
                (cls.BoneInitialPosChunk, 0x001)])
            # TODO add more chunks and their versions
        else:
            raise cls.CgfError("game %s not supported"%game)
        return [ version_dct[chunk.__class__] for chunk in chunks ]

    @classmethod
    def walk(cls, top,
             topdown = True, raisereaderror = False, verbose = 0):
        """A generator which yields the chunks and versions of all files in
        directory top whose filename matches the regular expression re_filename.
        The argument top can also be a file instead of a directory.
        The argument onerror, if set, will be called if cls.read raises an
        exception (errors coming from os.walk will be ignored)."""
        for filetype, fileversion, stream, chunks, versions \
            in cls.walkFile(top, topdown, raisereaderror, verbose):
            yield chunks, versions

    @classmethod
    def walkFile(cls, top,
                 topdown = True, raisereaderror = False, verbose = 0, mode = 'rb'):
        """Like walk, but returns more information:
        filetype, fileversion, f, chunks, and versions

        Note that the caller is not responsible for closing the file.

        walkFile is for instance used by runtest.py to implement the
        testFile-style tests which must access f after the file has been
        read."""
        # filter for recognizing cgf files by extension
        re_cgf = re.compile(r'^.*\.cgf$', re.IGNORECASE)
        # now walk over all these files in directory top
        for filename in Utils.walk(
            top, topdown, onerror = None, re_filename = re_cgf):
            
            if verbose >= 1:
                print "reading %s" % filename
            stream = open(filename, mode)
            try:
                # get the version
                filetype, fileversion = cls.getVersion(stream)
                if filetype >= 0:
                    # we got it, so now read the nif file
                    if verbose >= 2:
                        print("type 0x%08X, version 0x%08X"
                              %(filetype, fileversion))
                    try:
                        # return (filetype, fileversion, f, chunks, versions)
                        chunks, versions = cls.read(
                            stream, fileversion = fileversion)
                        yield filetype, fileversion, stream, chunks, versions
                    except StandardError:
                        # an error occurred during reading
                        # this should not happen: means that the file is
                        # corrupt, or that the xml is corrupt
                        # so we re-raise the exception if requested
                        if verbose >= 1:
                            print """\
Warning: read failed due to either a corrupt cgf file, a corrupt cgf.xml,
or a bug in CgfFormat library."""
                        if verbose >= 2:
                            Utils.hexDump(stream)
                        if raisereaderror:
                            raise
                # getting version failed, do not raise an exception
                # but tell user what happened
                elif filetype == -1:
                    if verbose >= 1:
                        print 'version not supported'
                else:
                    if verbose >= 1:
                        print 'not a cgf file'
            finally:
                stream.close()
