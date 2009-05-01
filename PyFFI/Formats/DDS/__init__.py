"""
.. :mod:`PyFFI.Formats.DDS` --- DirectDraw Surface (.dds)
   ======================================================

Regression tests
----------------

Read a DDS file
^^^^^^^^^^^^^^^

>>> # check and read dds file
>>> stream = open('tests/dds/test.dds', 'rb')
>>> data = DdsFormat.Data()
>>> data.inspect(stream)
>>> data.header.pixelFormat.size
32
>>> data.header.height
20
>>> data.read(stream)
>>> len(data.pixeldata.getValue())
888

Parse all DDS files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in DdsFormat.walkData('tests/dds'):
...     print(stream.name)
tests/dds/test.dds

Create a DDS file from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> data = DdsFormat.Data()
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> data.write(stream)

Get list of versions
^^^^^^^^^^^^^^^^^^^^

>>> for vnum in sorted(DdsFormat.versions.values()):
...     print('0x%08X' % vnum)
0x09000000
0x0A000000
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

import struct
import os
import re

import PyFFI.ObjectModels.xml
from PyFFI.ObjectModels import Common
from PyFFI.ObjectModels.xml.Basic import BasicBase
import PyFFI.ObjectModels
from PyFFI.Utils.Graph import EdgeFilter

class DdsFormat(PyFFI.ObjectModels.xml.FileFormat):
    """This class implements the DDS format."""
    xmlFileName = 'dds.xml'
    # where to look for dds.xml and in what order:
    # DDSXMLPATH env var, or DdsFormat module directory
    xmlFilePath = [os.getenv('DDSXMLPATH'), os.path.dirname(__file__)]
    # file name regular expression match
    RE_FILENAME = re.compile(r'^.*\.dds$', re.IGNORECASE)
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

        def getDetailDisplay(self):
            return self.__str__()

        def getHash(self, **kwargs):
            """Return a hash value for this value.

            :return: An immutable object that can be used as a hash.
            """
            return None

        def read(self, stream, **kwargs):
            """Read header string from stream and check it.

            :param stream: The stream to read from.
            :type stream: file
            """
            hdrstr = stream.read(4)
            # check if the string is correct
            if hdrstr != "DDS ":
                raise ValueError(
                    "invalid DDS header: expected 'DDS ' but got '%s'" % hdrstr)

        def write(self, stream, **kwargs):
            """Write the header string to stream.

            :param stream: The stream to write to.
            :type stream: file
            """
            stream.write("DDS ")

        def getSize(self, **kwargs):
            """Return number of bytes the header string occupies in a file.

            :return: Number of bytes.
            """
            return 4

    # exceptions
    class DdsError(StandardError):
        """Exception class used for DDS related exceptions."""
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        :param version_str: The version string.
        :type version_str: str
        :return: A version integer.

        >>> hex(DdsFormat.versionNumber('DX10'))
        '0xa000000'
        """
        return {'DX9': 0x09000000, 'DX10': 0x0A000000}[version_str]

    class Data(PyFFI.ObjectModels.FileFormat.Data):
        """A class to contain the actual dds data."""
        def __init__(self, version=0x09000000):
            self.version = version
            self.header = DdsFormat.Header()
            self.pixeldata = DdsFormat.PixelData()

            # TODO refactor xml model so we can get rid of these
            self.user_version = 0
            self.user_version2 = 0

        def inspectQuick(self, stream):
            """Quickly checks if stream contains DDS data, and gets the
            version, by looking at the first 8 bytes.

            :param stream: The stream to inspect.
            :type stream: file
            """
            pos = stream.tell()
            try:
                hdrstr = stream.read(4)
                if hdrstr != "DDS ":
                    raise ValueError("Not a DDS file.")
                size = struct.unpack("<I", stream.read(4))
                if size == 124:
                    self.version = 0x09000000 # DX9
                elif size == 144:
                    self.version = 0x0A000000 # DX10
            finally:
                stream.seek(pos)

        # overriding PyFFI.ObjectModels.FileFormat.Data methods

        def inspect(self, stream):
            """Quickly checks if stream contains DDS data, and reads the
            header.

            :param stream: The stream to inspect.
            :type stream: file
            """
            pos = stream.tell()
            try:
                self.inspectQuick(stream)
                self.header.read(stream, data=self)
            finally:
                stream.seek(pos)


        def read(self, stream, verbose=0):
            """Read a dds file.

            :param stream: The stream from which to read.
            :type stream: ``file``
            :param verbose: The level of verbosity.
            :type verbose: ``int``
            """
            # read the file
            self.inspectQuick(stream)
            self.header.read(stream, data=self)
            self.pixeldata.read(stream, data=self)

            # check if we are at the end of the file
            if stream.read(1) != '':
                raise self.DdsError(
                    'end of file not reached: corrupt dds file?')
            
        def write(self, stream, verbose=0):
            """Write a dds file.

            :param stream: The stream to which to write.
            :type stream: ``file``
            :param verbose: The level of verbosity.
            :type verbose: ``int``
            """
            # TODO: make sure pixel data has correct length

            # write the file
            # first header
            self.header.write(stream, data=self)
            # next the pixel data
            self.pixeldata.write(stream, data=self)

        # DetailNode

        def getDetailChildNodes(self, edge_filter=EdgeFilter()):
            return self.header.getDetailChildNodes(edge_filter=edge_filter)

        def getDetailChildNames(self, edge_filter=EdgeFilter()):
            return self.header.getDetailChildNames(edge_filter=edge_filter)
