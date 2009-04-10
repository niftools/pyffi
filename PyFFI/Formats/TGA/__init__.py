"""
This module implements the TGA file format.

Examples
========

Read a TGA file
---------------

>>> # check and read tga file
>>> f = open('tests/tga/test.tga', 'rb')
>>> version = TgaFormat.getVersion(f)
>>> if version == -1:
...     raise RuntimeError('tga version not supported')
... elif version == -2:
...     raise RuntimeError('not a tga file')
>>> header, data = TgaFormat.read(f, version = version)
>>> # get TGA header
>>> header.width
60
>>> header.height
20

Parse all TGA files in a directory tree
---------------------------------------

>>> for header, data in TgaFormat.walk('tests/tga',
...                                    raisereaderror = False,
...                                    verbose = 1):
...     pass
reading tests/tga/test.tga

Create a TGA file from scratch and write to file
------------------------------------------------

>>> header = TgaFormat.Header()
>>> from tempfile import TemporaryFile
>>> f = TemporaryFile()
>>> TgaFormat.write(f, version = version, header = header,
...                 pixeldata = TgaFormat.PixelData())
"""

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

import struct, os, re

from PyFFI.ObjectModels.XML.FileFormat import XmlFileFormat
from PyFFI.ObjectModels.XML.FileFormat import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI.ObjectModels import Common
from PyFFI.ObjectModels.XML.Basic import BasicBase

class TgaFormat(XmlFileFormat):
    """This class implements the TGA format."""
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'tga.xml'
    # where to look for tga.xml and in what order:
    # TGAXMLPATH env var, or TgaFormat module directory
    xmlFilePath = [ os.getenv('TGAXMLPATH'), os.path.dirname(__file__) ]
    # path of class customizers
    clsFilePath = os.path.dirname(__file__)
    # used for comparing floats
    _EPSILON = 0.0001
    # filter for recognizing tga files by extension
    RE_FILENAME = re.compile(r'^.*\.tga$', re.IGNORECASE)

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

    # exceptions
    class TgaError(StandardError):
        """Exception class used for TGA related exceptions."""
        pass

    @classmethod
    def getVersion(cls, stream):
        """Get version and user version.

        Returns (0, 0) if the file looks like a TGA file, (-1, 0) if it is
        a TGA file but the format is not supported, and (-2, 0) if it is not a
        TGA file.

        @param stream: The stream from which to read.
        @type stream: file
        @return: (0, 0) for TGA files, (-2, 0) for non-TGA files.
        """
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
            return -2, 0
        finally:
            stream.seek(pos)
        # check if tga type is valid
        if not image_type in (1, 2, 3, 9, 10, 11):
            return -2, 0
        # check pixel size
        if not pixel_size in (8, 24, 32):
            return -2, 0
        # check width and height
        if width >= 100000 or height >= 100000:
            return -2, 0
        # this looks like a tga file
        return 0, 0

    @classmethod
    def read(cls, stream, version = None, user_version = None, verbose = 0):
        """Read a tga file.

        @param stream: The stream from which to read.
        @type stream: file
        @param version: The TGA version obtained by L{getVersion}.
        @type version: int
        @param user_version: The TGA user version obtained by L{getVersion}.
        @type user_version: int
        @param verbose: The level of verbosity.
        @type verbose: int
        @return: header, pixeldata
        """
        # read the file
        header = cls.Header()
        header.read(stream, version = version, user_version = user_version)
        pixeldata = cls.PixelData()
        pixeldata.read(stream, version = version, user_version = user_version)

        # check if we are at the end of the file
        if stream.read(1) != '':
            raise cls.TgaError('end of file not reached: corrupt tga file?')

        return header, pixeldata

    @classmethod
    def write(cls, stream, version = None, user_version = None,
              header = None, pixeldata = None,
              verbose = 0):
        """Write a tga file.

        @param stream: The stream to which to write.
        @type stream: file
        @param version: The version number (usually 0).
        @type version: int
        @param user_version: The user version number (usually 0).
        @type user_version: int
        @param header: The tga header.
        @type header: L{TgaFormat.Header}
        @param pixeldata: The tga pixel data.
        @type pixeldata: L{TgaFormat.PixelData}
        @param verbose: The level of verbosity.
        @type verbose: int
        """
        # TODO: make sure pixel data has correct length

        # write the file
        # first header
        assert(isinstance(header, cls.Header))
        header.write(stream, version = version, user_version = user_version)
        # next the pixel data
        assert(isinstance(pixeldata, cls.PixelData))
        pixeldata.write(stream, version = version, user_version = user_version)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

