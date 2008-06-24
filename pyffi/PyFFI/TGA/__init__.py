"""
This module implements the TGA file format.

Examples
========

Read a TGA file
---------------

>>> # check and read tga file
>>> f = open('test.tga', 'rb')
>>> version = TgaFormat.getVersion(f)
>>> if version == -1:
...     raise RuntimeError('tga version not supported')
... elif version == -2:
...     raise RuntimeError('not a tga file')
>>> header, data = TgaFormat.read(f, version = version)
>>> # print TGA header
>>> print header.width, header.height
60 20

Create a TGA file from scratch and write to file
------------------------------------------------

>>> header = TgaFormat.Header()
>>> from tempfile import TemporaryFile
>>> f = TemporaryFile()
>>> TgaFormat.write(f, version = version, header = header, pixeldata = TgaFormat.PixelData())
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

class TgaFormat(object):
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'tga.xml'
    # where to look for tga.xml and in what order:
    # TGAXMLPATH env var, or TgaFormat module directory
    xmlFilePath = [ os.getenv('TGAXMLPATH'), os.path.dirname(__file__) ]
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

    # implementation of tga-specific basic types

    class PixelData(BasicBase):
        """Basic type for pixel data."""
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)
            self.setValue('')

        def getValue(self):
            return self._value

        def setValue(self, value):
            if len(value) > 16000000:
                raise ValueError('pixel data too long')
            self._value = str(value)

        def __str__(self):
            return '<PIXEL DATA>'

        def getSize(self, **kwargs):
            return len(self._value)

        def getHash(self, **kwargs):
            return self.getValue()

        def read(self, stream, **kwargs):
            self._value = stream.read(-1)

        def write(self, stream, **kwargs):
            stream.write(self._value)

    # exceptions
    class TgaError(StandardError):
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer. TGA files have no versions
        so this function simply raises NotImplementedError."""
        # TGA format not versioned
        raise NotImplementedError

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable
        by python.

        >>> TgaFormat.nameAttribute('tHis is A Silly naME')
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
        """Returns 0 if the file looks like a TGA file, -1 if it is a TGA file
        but the format is not supported, and -2 if it is not a TGA file.

        @param stream: The stream from which to read, typically a file or a
            memory stream such as cStringIO.
        @return: 0 for TGA files, -2 for non-TGA files.
        """
        #return 0
        pos = stream.tell()
        # read header
        try:
            id_length, colormap_type, image_type, \
            colormap_index, colormap_length, colormap_size, \
            x_origin, y_origin, width, height, \
            pixel_size, flags = struct.unpack("<BBBHHBHHHHBB", stream.read(18))
        except struct.error:
            # could not read 18 bytes
            # not a TGA file
            return -2
        finally:
            stream.seek(pos)
        # check if tga type is valid
        if not image_type in (1, 2, 3, 9, 10, 11):
            return -2
        # check pixel size
        if not pixel_size in (8, 24, 32):
            return -2
        # check width and height
        if width >= 100000 or height >= 100000:
            return -2
        # this looks like a tga file
        return 0

    @classmethod
    def read(cls, stream, version = None, verbose = 0):
        """Read a tga file.

        @param stream: The stream from which to read, typically a file or a
            memory stream such as cStringIO.
        @param version: The TGA version.
        @param verbose: The level of verbosity."""
        # read the file
        header = cls.Header()
        header.read(stream, version = version)
        pixeldata = cls.PixelData()
        pixeldata.read(stream, version = version)

        # check if we are at the end of the file
        if stream.read(1) != '':
            raise cls.TgaError('end of file not reached: corrupt tga file?')

        return header, pixeldata

    @classmethod
    def write(cls, stream, version = None,
              header = None, pixeldata = None, verbose = 0):
        # TODO: make sure pixel data has correct length

        # write the file
        # first header
        assert(isinstance(header, cls.Header))
        header.write(stream, version = version)
        # next the pixel data
        assert(isinstance(pixeldata, cls.PixelData))
        pixeldata.write(stream, version = version)

    @classmethod
    def walk(cls, top, topdown = True, onerror = None, verbose = 0):
        """A generator which yields the roots of all files in directory top
        whose filename matches the regular expression re_filename. The argument
        top can also be a file instead of a directory. The argument onerror,
        if set, will be called if cls.read raises an exception (errors coming
        from os.walk will be ignored)."""
        for version, f, tga in cls.walkFile(top, topdown, onerror, verbose):
            yield tga

    @classmethod
    def walkFile(cls, top, topdown = True,
                 raisereaderror = False, verbose = 0, mode = 'rb'):
        """Like walk, but returns more information:
        version, f, and tga.

        Note that the caller is not responsible for closing stream.

        walkFile is for instance used by runtest.py to implement the
        testFile-style tests which must access the file after the file has been
        read."""
        # filter for recognizing tga files by extension
        re_tga = re.compile(r'^.*\.tga$', re.IGNORECASE)
        # now walk over all these files in directory top
        for filename in Utils.walk(top, topdown, onerror = None,
                                   re_filename = re_tga):
            if verbose >= 1: print "reading %s"%filename
            stream = open(filename, mode)
            try:
                # get the version
                version = cls.getVersion(stream)
                if version >= 0:
                    # we got it, so now read the tga file
                    if verbose >= 2: print "version 0x%08X"%version
                    try:
                        # return (version, stream, (header, pixeldata))
                        yield (version, stream,
                               cls.read(stream, version = version))
                    except StandardError:
                        # an error occurred during reading
                        # this should not happen: means that the file is
                        # corrupt, or that the xml is corrupt
                        if verbose >= 1:
                            print """
Warning: read failed due to either a corrupt tga file, a corrupt tga.xml,
or a bug in TgaFormat library."""
                        if verbose >= 2:
                            Utils.hexDump(stream)
                        if raisereaderror:
                            raise
                # getting version failed, do not raise an exception
                # but tell user what happened
                elif version == -1:
                    if verbose >= 1: print 'version not supported'
                else:
                    if verbose >= 1: print 'not a tga file'
            finally:
                stream.close()

if __name__=='__main__':
    import doctest
    doctest.testmod()

