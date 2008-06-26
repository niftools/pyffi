"""
This module implements the DDS file format.

Examples
========

Read a DDS file
---------------

>>> # check and read dds file
>>> f = open('tests/dds/test.dds', 'rb')
>>> version = DdsFormat.getVersion(f)
>>> if version == -1:
...     raise RuntimeError('dds version not supported')
... elif version == -2:
...     raise RuntimeError('not a dds file')
>>> header, data = DdsFormat.read(f, version = version)
>>> # print DDS header
>>> print header.size
124
>>> print header.pixelFormat.size
32

Create a DDS file from scratch and write to file
------------------------------------------------

>>> header = DdsFormat.Header()
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> DdsFormat.write(stream, version = version, header = header,
...                 pixeldata = DdsFormat.PixelData())

Get list of versions
--------------------

>>> for vnum in sorted(DdsFormat.versions.values()):
...     print '0x%08X'%vnum
0x00000009
0x00000010
"""

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

import struct, os, re

from PyFFI import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI import Common
from PyFFI.Bases.Basic import BasicBase

class DdsFormat(object):
    """This class implements the DDS format."""
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'dds.xml'
    # where to look for dds.xml and in what order:
    # DDSXMLPATH env var, or DdsFormat module directory
    xmlFilePath = [ os.getenv('DDSXMLPATH'), os.path.dirname(__file__) ]
    # path of class customizers
    clsFilePath = os.path.dirname(__file__)
    # used for comparing floats
    _EPSILON = 0.0001

    # basic types
    int = Common.Int
    uint = Common.UInt
    byte = Common.Byte
    ubyte = Common.UByte
    char = Common.Char
    short = Common.Short
    ushort = Common.UShort
    float = Common.Float
    PixelData = Common.UndecodedData

    # implementation of dds-specific basic types

    class HeaderString(BasicBase):
        """Basic type which implements the header of a DDS file."""
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)

        def __str__(self):
            return 'DDS'

        def getHash(self, **kwargs):
            """Return a hash value for this value.

            @return: An immutable object that can be used as a hash.
            """
            return None

        def read(self, stream, **kwargs):
            """Read header string from stream and check it.

            @param stream: The stream to read from.
            @type stream: file
            """
            hdrstr = stream.read(4)
            # check if the string is correct
            if hdrstr != "DDS ":
                raise ValueError(
                    "invalid DDS header: expected 'DDS ' but got '%s'" % hdrstr)

        def write(self, stream, **kwargs):
            """Write the header string to stream.

            @param stream: The stream to write to.
            @type stream: file
            """
            stream.write("DDS ")

        def getSize(self, **kwargs):
            """Return number of bytes the header string occupies in a file.

            @return: Number of bytes.
            """
            return 4

    # exceptions
    class DdsError(StandardError):
        """Exception class used for DDS related exceptions."""
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        @param version_str: The version string.
        @type version_str: str
        @return: A version integer.

        >>> hex(DdsFormat.versionNumber('DX10'))
        '0x10'
        """
        return { 'DX9' : 0x09, 'DX10' : 0x10 }[version_str]

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable
        by python.

        @param name: The attribute name.
        @type name: str
        @return: Reformatted attribute name, useable by python.

        >>> DdsFormat.nameAttribute('tHis is A Silly naME')
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
        """Returns 0 if the file is a DDS file, -1 if it is not supported, and
        -2 if it is not a DDS file.

        @param stream: The stream from which to read.
        @type stream: file
        @return: 0 for DDS files, -2 for non-DDS files.
        """
        pos = stream.tell()
        try:
            hdrstr = stream.read(4)
        finally:
            stream.seek(pos)
        if hdrstr != "DDS ":
            return -2
        return 0x09 # TODO DX10

    @classmethod
    def read(cls, stream, version = None, verbose = 0):
        """Read a dds file.

        @param stream: The stream from which to read.
        @type stream: file
        @param version: The DDS version obtained by L{getVersion}.
        @type version: int
        @param verbose: The level of verbosity.
        @type verbose: int
        @return: header, pixeldata
        """
        # read the file
        header = cls.Header()
        header.read(stream, version = version)
        pixeldata = cls.PixelData()
        pixeldata.read(stream, version = version)

        # check if we are at the end of the file
        if stream.read(1) != '':
            raise cls.DdsError('end of file not reached: corrupt dds file?')

        return header, pixeldata

    @classmethod
    def write(cls, stream, version = None,
              header = None, pixeldata = None, verbose = 0):
        """Write a dds file.

        @param stream: The stream to which to write.
        @type stream: file
        @param version: The version number (9 or 10).
        @type version: int
        @param header: The dds header.
        @type header: L{DdsFormat.Header}
        @param pixeldata: The dds pixel data.
        @type pixeldata: L{DdsFormat.PixelData}
        @param verbose: The level of verbosity.
        @type verbose: int
        """
        # TODO: make sure pixel data has correct length

        # write the file
        # first header
        assert(isinstance(header, cls.Header))
        header.write(stream, version = version)
        # next the pixel data
        assert(isinstance(pixeldata, cls.PixelData))
        pixeldata.write(stream, version = version)

    @classmethod
    def walk(cls, top, topdown = True, raisereaderror = False, verbose = 0):
        """A generator which yields (header, pixeldata) of all files in
        directory top whose filename matches the regular expression
        re_filename. The argument top can also be a file instead of a
        directory. Errors coming from os.walk are ignored.

        >>> for header, pixeldata in DdsFormat.walk('tests/dds',
        ...                                         raisereaderror = True,
        ...                                         verbose = 1):
        ...     pass
        reading tests/dds/test.dds

        @param top: The top folder.
        @type top: str
        @param topdown: Determines whether subdirectories should be iterated
            over first.
        @type topdown: bool
        @param raisereaderror: Should read errors raise an exception, or
            should they be ignored?
        @type raisereaderror: bool
        @param verbose: Verbosity level.
        @type verbose: int
        """
        for version, stream, header, pixeldata in cls.walkFile(
            top, topdown = topdown,
            raisereaderror = raisereaderror, verbose = verbose):
            yield header, pixeldata

    @classmethod
    def walkFile(cls, top, topdown = True,
                 raisereaderror = False, verbose = 0, mode = 'rb'):
        """Like L{walk}, but returns more information:
        version, stream, header, and pixeldata.

        Note that the caller is not responsible for closing stream.

        walkFile is for instance used by runtest.py to implement the
        testFile-style tests which must access the file after the file has been
        read.

        @param top: The top folder.
        @type top: str
        @param topdown: Determines whether subdirectories should be iterated
            over first.
        @type topdown: bool
        @param raisereaderror: Should read errors raise an exception, or
            should they be ignored?
        @type raisereaderror: bool
        @param verbose: Verbosity level.
        @type verbose: int
        """
        # filter for recognizing dds files by extension
        re_dds = re.compile(r'^.*\.dds$', re.IGNORECASE)
        # now walk over all these files in directory top
        for filename in Utils.walk(top, topdown, onerror = None,
                                   re_filename = re_dds):
            if verbose >= 1:
                print("reading %s" % filename)
            stream = open(filename, mode)
            try:
                # get the version
                version = cls.getVersion(stream)
                if version >= 0:
                    # we got it, so now read the dds file
                    if verbose >= 2:
                        print("version 0x%08X" % version)
                    try:
                        # return (version, stream, (header, pixeldata))
                        yield ((version, stream) +
                               cls.read(stream, version = version))
                    except StandardError:
                        # an error occurred during reading
                        # this should not happen: means that the file is
                        # corrupt, or that the xml is corrupt
                        if verbose >= 1:
                            print("""
Warning: read failed due to either a corrupt dds file, a corrupt dds.xml,
or a bug in DdsFormat library.""")
                        if verbose >= 2:
                            Utils.hexDump(stream)
                        if raisereaderror:
                            raise
                # getting version failed, do not raise an exception
                # but tell user what happened
                elif version == -1:
                    if verbose >= 1:
                        print('version not supported')
                else:
                    if verbose >= 1:
                        print('not a dds file')
            finally:
                stream.close()
