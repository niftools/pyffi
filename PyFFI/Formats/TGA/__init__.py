"""
:mod:`PyFFI.Formats.TGA` --- Targa (.tga)
=========================================

Regression tests
----------------

Read a TGA file
^^^^^^^^^^^^^^^

>>> # check and read tga file
>>> stream = open('tests/tga/test.tga', 'rb')
>>> data = TgaFormat.Data()
>>> data.inspect(stream)
>>> data.read(stream)
>>> stream.close()
>>> data.width
60
>>> data.height
20

Parse all TGA files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in TgaFormat.walkData('tests/tga'):
...     print(stream.name)
tests/tga/test.tga

Create a TGA file from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> data = TgaFormat.Data()
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> data.write(stream)
>>> stream.close()
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

import PyFFI.ObjectModels.xml
import PyFFI.ObjectModels.Common
import PyFFI.ObjectModels.xml.Struct
import PyFFI.ObjectModels
from PyFFI.Utils.Graph import EdgeFilter

class TgaFormat(PyFFI.ObjectModels.xml.FileFormat):
    """This class implements the TGA format."""
    xmlFileName = 'tga.xml'
    # where to look for tga.xml and in what order:
    # TGAXMLPATH env var, or TgaFormat module directory
    xmlFilePath = [os.getenv('TGAXMLPATH'), os.path.dirname(__file__)]
    # filter for recognizing tga files by extension
    RE_FILENAME = re.compile(r'^.*\.tga$', re.IGNORECASE)

    # basic types
    int = PyFFI.ObjectModels.Common.Int
    uint = PyFFI.ObjectModels.Common.UInt
    byte = PyFFI.ObjectModels.Common.Byte
    ubyte = PyFFI.ObjectModels.Common.UByte
    char = PyFFI.ObjectModels.Common.Char
    short = PyFFI.ObjectModels.Common.Short
    ushort = PyFFI.ObjectModels.Common.UShort
    float = PyFFI.ObjectModels.Common.Float
    PixelData = PyFFI.ObjectModels.Common.UndecodedData

    class Header(PyFFI.ObjectModels.FileFormat.Data):
        def inspect(self, stream):
            """Quick heuristic check if stream contains Targa data,
            by looking at the first 18 bytes.

            :param stream: The stream to inspect.
            :type stream: file
            """
            # XXX todo: set some of the actual fields

            pos = stream.tell()
            # read header
            try:
                id_length, colormap_type, image_type, \
                colormap_index, colormap_length, colormap_size, \
                x_origin, y_origin, width, height, \
                pixel_size, flags = struct.unpack("<BBBHHBHHHHBB",
                                                  stream.read(18))
            except struct.error:
                # could not read 18 bytes
                # not a TGA file
                raise ValueError("Not a Targa file.")
            finally:
                stream.seek(pos)
            # check if tga type is valid
            # check pixel size
            # check width and height
            if not(image_type in (1, 2, 3, 9, 10, 11)
                   and pixel_size in (8, 24, 32)
                   and width <= 100000
                   and height <= 100000):
                raise ValueError("Not a Targa file.")
            # this looks like a tga file!

        def read(self, stream):
            """Read a tga file.

            :param stream: The stream from which to read.
            :type stream: ``file``
            """
            # read the file
            self.inspect(stream) # quick check
            PyFFI.ObjectModels.xml.Struct.StructBase.read(self, stream)

            # check if we are at the end of the file
            if stream.read(1) != '':
                raise ValueError(
                    'end of file not reached: corrupt tga file?')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
