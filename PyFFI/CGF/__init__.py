# --------------------------------------------------------------------------
# PyFFI.CGF
# Implementation of the CGF file format.
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

from PyFFI import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI import Common
from PyFFI.Bases.Basic import BasicBase

class CgfFormat(object):
    """Stores all information about the cgf file format."""
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'cgf.xml'
    xmlFilePath = [ os.getenv('CGFXMLPATH'), os.path.dirname(__file__) ] # where to look for cgf.xml and in what order: CGFXMLPATH env var, or module directory
    clsFilePath = os.path.dirname(__file__) # path of class customizers
    _EPSILON = 0.0001 # used for comparing floats
    
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
        def __init__(self, template = None, argument = None):
            pass

        def __str__(self):
            return 'CryTek\x00\x00'

        def read(self, f = None, **kwargs):
            s = f.read(8)
            if s[:6] != self.__str__()[:6]:
                raise ValueError("invalid CGF header: expected '%s' but got '%s'"%(self.__str__(), s))

        def write(self, f = None, **kwargs):
            f.write(self.__str__())

    class String(BasicBase):
        def __init__(self, **kwargs):
            self._x = ""

        def __str__(self):
            if not self._x: return '<EMPTY STRING>'
            return self._x

        def getValue(self):
            return self._x

        def setValue(self, value):
            s = str(value)
            i = s.find('\x00')
            if i != -1:
                s = s[:i]
            self._x = s

        def read(self, f = None, **kwargs):
            self._x = ''
            c = ''
            while c != '\x00':
                self._x += c
                c = f.read(1)

        def write(self, f = None, **kwargs):
            f.write(self._x)
            f.write('\x00')

    class String32(BasicBase):
        _len = 32
        
        def __init__(self, **kwargs):
            self._x = ""

        def __str__(self):
            if not self._x: return '<EMPTY STRING>'
            return self._x

        def getValue(self):
            return self._x

        def setValue(self, value):
            s = str(value)
            if len(s) > self._len:
                raise ValueError("string '%s' too long"%self._x)
            self._x = s

        def read(self, f = None, **kwargs):
            self._x = f.read(self._len)
            i = self._x.find('\x00')
            if i != -1:
                self._x = self._x[:i]

        def write(self, f = None, **kwargs):
            f.write(self._x.ljust(self._len, "\x00"))

    class String64(String32):
        _len = 64

    class String128(String32):
        _len = 128

    class String256(String32):
        _len = 256

    class Ref(BasicBase):
        _isTemplate = True
        _hasLinks = True
        _hasRefs = True
        def __init__(self, template = type(None), **kwargs):
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

        def read(self, f = None, link_stack = [], **kwargs):
            self._x = None # fixLinks will set this field
            block_index, = struct.unpack('<i', f.read(4))
            link_stack.append(block_index)

        def write(self, f = None, block_index_dct = {}, **kwargs):
            if self._x == None:
                f.write('\xff\xff\xff\xff')
            else:
                f.write(struct.pack('<i', block_index_dct[self._x]))

        def fixLinks(self, block_dct = [], link_stack = [], **kwargs):
            block_index = link_stack.pop(0)
            # case when there's no link
            if block_index == -1:
                self._x = None
                return
            # other case: look up the link and check the link type
            try:
                block = block_dct[block_index]
            except KeyError:
                # make this raise an exception when all reference errors
                # are sorted out
                print "WARNING: invalid chunk reference (%i)"%block_index
                self._x = None
                return
            if not isinstance(block, self._template):
                # make this raise an exception when all reference errors
                # are sorted out
                print 'WARNING: expected an instance of %s but got instance of %s'%(self._template, block.__class__)
            self._x = block

        def getLinks(self, **kwargs):
            if self._x != None:
                return [self._x]
            else:
                return []

        def getRefs(self):
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

        def getRefs(self):
            return []

    # exceptions
    class CgfError(StandardError):
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
        
        parts = str(name).split() # str(name) converts name to string in case name is a unicode string
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    @classmethod
    def getVersion(cls, f):
        """Returns file type (geometry or animation) and version of the
        chunk table.

        Returns -1, 0 if file type or chunk table version is not supported.
        Returns -2, 0 if <f> is not a cgf file.
        """
        pos = f.tell()
        try:
            s = f.read(8)
            filetype, fileversion = struct.unpack('<II', f.read(8))
        except StandardError:
            return -2, 0
        finally:
            f.seek(pos)
        if s[:6] != "CryTek":
            return -2, 0
        if filetype not in [ cls.FileType.GEOM, cls.FileType.ANIM ]:
            return -1, 0
        if fileversion not in cls.versions.values():
            return -1, 0
        return filetype, fileversion

    @classmethod
    def read(cls, fileversion, f, verbose = 0):
        chunk_types = [x for x in dir(cls.ChunkType) if x[:2] != '__']

        # read header
        hdr = cls.Header()
        hdr.read(fileversion, f = f)

        # read chunk table
        f.seek(hdr.offset)
        table = cls.ChunkTable()
        table.read(version = hdr.version, f = f)

        # read the chunks
        link_stack = [] # list of chunk identifiers, as they are added to the stack
        chunk_dct = {} # maps chunk index to actual chunk
        chunks = [] # records all chunks as read from cgf file in proper order
        versions = [] # records all chunk versions as read from cgf file
        for chunkhdr in table.chunkHeaders:
            # check that id is unique
            if chunk_dct.has_key(chunkhdr.id):
                raise ValueError('chunk id %i not unique'%chunkhdr.id)

            # get chunk type
            for s in chunk_types:
                if getattr(cls.ChunkType, s) == chunkhdr.type: break
            else:
                raise ValueError('unknown chunk type 0x%08X'%chunkhdr.type)
            #print "%s chunk, version 0x%08X"%(s,chunkhdr.version)
            try:
                chunk = getattr(cls, s + 'Chunk')()
            except AttributeError:
                raise ValueError('undecoded chunk type 0x%08X (%sChunk)'%(chunkhdr.type, s))

            # now read the chunk
            f.seek(chunkhdr.offset)

            # most chunks start with a copy of chunkhdr
            if chunkhdr.type not in [cls.ChunkType.SourceInfo, cls.ChunkType.BoneNameList, cls.ChunkType.BoneLightBinding, cls.ChunkType.BoneInitialPos, cls.ChunkType.MeshMorphTarget]:
                chunkhdr_copy = cls.ChunkHeader()
                chunkhdr_copy.read(version = hdr.version, f = f)
                # check that the copy is valid
                if chunkhdr_copy.type != chunkhdr.type or chunkhdr_copy.version != chunkhdr.version or chunkhdr_copy.offset != chunkhdr.offset or chunkhdr_copy.id != chunkhdr.id:
                    raise ValueError('chunk starts with invalid header:\nexpected\n%sbut got\n%s'%(chunkhdr, chunkhdr_copy))

            chunk.read(version = chunkhdr.version, f = f, link_stack = link_stack)
            chunks.append(chunk)
            versions.append(chunkhdr.version)
            chunk_dct[chunkhdr.id] = chunk

        # fix links
        for chunk, version in zip(chunks, versions):
            #print chunk.__class__
            chunk.fixLinks(version = version, block_dct = chunk_dct, link_stack = link_stack)
        if link_stack != []:
            raise cls.CgfError('not all links have been popped from the stack (bug?)')

        return chunks, versions

    @classmethod
    def write(cls, filetype, fileversion, f, chunks, versions, verbose = 0):
        chunk_types = [x for x in dir(cls.ChunkType) if x[:2] != '__']

        # write header
        hdr = cls.Header()
        hdr.type = filetype
        hdr.version = fileversion
        hdr.offset = -1 # set this at the end
        hdr.write(version = fileversion, f = f)

        # write chunks and add headers to chunk table
        table = cls.ChunkTable()

        # write chunk table
        hdr.offset = f.tell()
        table.write(version = fileversion, f = f)

    @classmethod
    def walk(cls, top, topdown = True, onerror = None, verbose = 0):
        """A generator which yields the chunks and versions of all files in directory top
        whose filename matches the regular expression re_filename. The argument
        top can also be a file instead of a directory. The argument onerror,
        if set, will be called if cls.read raises an exception (errors coming
        from os.walk will be ignored)."""
        for filetype, fileversion, f, chunks, versions in walkFile(cls, top, topdown, onerror, verbose):
            yield chunks, versions

    @classmethod
    def walkFile(cls, top, topdown = True, onerror = None, verbose = 0, mode = 'rb'):
        """Like walk, but returns more information:
        filetype, fileversion, f, chunks, and versions

        Note that the caller is not responsible for closing f.

        walkFile is for instance used by runtest.py to implement the
        testFile-style tests which must access f after the file has been read."""
        # filter for recognizing cgf files by extension
        re_cgf = re.compile(r'^.*\.cgf$', re.IGNORECASE)
        # now walk over all these files in directory top
        for filename in Utils.walk(top, topdown, onerror = None, re_filename = re_cgf):
            if verbose >= 1: print "reading %s"%filename
            f = open(filename, mode)
            try:
                # get the version
                filetype, fileversion = cls.getVersion(f)
                if filetype >= 0:
                    # we got it, so now read the nif file
                    if verbose >= 2: print "type 0x%08X, version 0x%08X"%(filetype, fileversion)
                    try:
                        # return (filetype, fileversion, f, chunks, versions)
                        chunks, versions = cls.read(fileversion, f)
                        yield filetype, fileversion, f, chunks, versions
                    except NotImplementedError: #StandardError, e:
                        # an error occurred during reading
                        # this should not happen: means that the file is
                        # corrupt, or that the xml is corrupt
                        # so we call onerror
                        if verbose >= 1:
                            print 'Warning: read failed due to either a corrupt cgf file, a corrupt cgf.xml,'
                            print 'or a bug in CgfFormat library.'
                        if verbose >= 2:
                            Utils.hexDump(f)
                        if onerror == None:
                            pass # ignore the error
                        else:
                            onerror(e)
                # getting version failed, do not raise an exception
                # but tell user what happened
                elif filetype == -1:
                    if verbose >= 1: print 'version not supported'
                else:
                    if verbose >= 1: print 'not a cgf file'
            finally:
                f.close()
