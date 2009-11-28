"""
:mod:`pyffi.formats.tri` --- TRI (.tri)
=======================================

A .tri file contains facial expression data, that is, morphs for dynamic
expressions such as smile, frown, and so on.

Implementation
--------------

.. autoclass:: TriFormat
   :show-inheritance:
   :members:

Regression tests
----------------

Read a TRI file
^^^^^^^^^^^^^^^

>>> # check and read tri file
>>> stream = open('tests/tri/mmouthxivilai.tri', 'rb')
>>> data = TriFormat.Data()
>>> data.inspect(stream)
>>> # do some stuff with header?
>>> #data.header....
>>> data.read(stream) # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
ValueError: end of file not reached: corrupt tri file?
>>> # do some stuff...

Parse all TRI files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in TriFormat.walkData('tests/tri'):
...     print(stream.name)
tests/tri/mmouthxivilai.tri

Create an TRI file from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> data = TriFormat.Data()
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> data.write(stream)
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

import pyffi.object_models.xml
import pyffi.object_models.common
from pyffi.object_models.xml.basic import BasicBase
import pyffi.object_models
from pyffi.utils.graph import EdgeFilter

class TriFormat(pyffi.object_models.xml.FileFormat):
    """This class implements the TRI format."""
    xml_file_name = 'tri.xml'
    # where to look for tri.xml and in what order:
    # TRIXMLPATH env var, or TriFormat module directory
    xmlFilePath = [os.getenv('TRIXMLPATH'), os.path.dirname(__file__)]
    # file name regular expression match
    RE_FILENAME = re.compile(r'^.*\.tri$', re.IGNORECASE)
    # used for comparing floats
    _EPSILON = 0.0001

    # basic types
    int = pyffi.object_models.common.Int
    uint = pyffi.object_models.common.UInt
    byte = pyffi.object_models.common.Byte
    ubyte = pyffi.object_models.common.UByte
    char = pyffi.object_models.common.Char
    short = pyffi.object_models.common.Short
    ushort = pyffi.object_models.common.UShort
    float = pyffi.object_models.common.Float

    # implementation of tri-specific basic types

    class FileSignature(BasicBase):
        """Basic type which implements the header of a TRI file."""
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)

        def __str__(self):
            return 'FRTRI'

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
            hdrstr = stream.read(5)
            # check if the string is correct
            if hdrstr != "FRTRI".encode("ascii"):
                raise ValueError(
                    "invalid TRI header: expected 'FRTRI' but got '%s'" % hdrstr)

        def write(self, stream, **kwargs):
            """Write the header string to stream.

            :param stream: The stream to write to.
            :type stream: file
            """
            stream.write("FREGM".encode("ascii"))

        def getSize(self, **kwargs):
            """Return number of bytes the header string occupies in a file.

            :return: Number of bytes.
            """
            return 5

    class FileVersion(BasicBase):
        def getValue(self):
            raise NotImplementedError

        def setValue(self, value):
            raise NotImplementedError

        def __str__(self):
            return 'XXX'

        def getSize(self, **kwargs):
            return 3

        def getHash(self, **kwargs):
            return None

        def read(self, stream, **kwargs):
            ver = stream.read(3)
            if ver != '%03i' % kwargs['data'].version:
                raise ValueError(
                    "Invalid version number: expected %03i but got %s."
                    % (kwargs['data'].version, ver))

        def write(self, stream, **kwargs):
            stream.write('%03i' % kwargs['data'].version)

        def getDetailDisplay(self):
            return 'XXX'

    # XXX nothing here yet...

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        :param version_str: The version string.
        :type version_str: str
        :return: A version integer.

        >>> TriFormat.versionNumber('003')
        3
        >>> TriFormat.versionNumber('XXX')
        -1
        """
        try:
            # note: always '003' in all files seen so far
            return int(version_str)
        except ValueError:
            # not supported
            return -1

    class Data(pyffi.object_models.FileFormat.Data):
        """A class to contain the actual tri data."""
        def __init__(self):
            pass

        def inspectQuick(self, stream):
            """Quickly checks if stream contains TRI data, and gets the
            version, by looking at the first 8 bytes.

            :param stream: The stream to inspect.
            :type stream: file
            """
            pos = stream.tell()
            try:
                hdrstr = stream.read(5)
                if hdrstr != "FRTRI".encode("ascii"):
                    raise ValueError("Not a TRI file.")
            finally:
                stream.seek(pos)

        # overriding pyffi.object_models.FileFormat.Data methods

        def inspect(self, stream):
            """Quickly checks if stream contains TRI data, and reads the
            header.

            :param stream: The stream to inspect.
            :type stream: file
            """
            pos = stream.tell()
            try:
                self.inspectQuick(stream)
                # XXX read header
            finally:
                stream.seek(pos)


        def read(self, stream):
            """Read a tri file.

            :param stream: The stream from which to read.
            :type stream: ``file``
            """
            self.inspectQuick(stream)
            # XXX read the file

            # check if we are at the end of the file
            if stream.read(1):
                raise ValueError(
                    'end of file not reached: corrupt tri file?')
            
        def write(self, stream):
            """Write a tri file.

            :param stream: The stream to which to write.
            :type stream: ``file``
            """
            # XXX write the file

        # DetailNode

        def getDetailChildNodes(self, edge_filter=EdgeFilter()):
            return []
            # XXX todo, for instance:
            #return self.header.getDetailChildNodes(edge_filter=edge_filter)

        def getDetailChildNames(self, edge_filter=EdgeFilter()):
            return []
            # XXX todo, for instance:
            #return self.header.getDetailChildNames(edge_filter=edge_filter)
