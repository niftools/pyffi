"""
:mod:`pyffi.formats.bsa` --- Bethesda Archive (.bsa)
====================================================

A .bsa file is an archive format used by Bethesda (Morrowind, Oblivion,
Fallout 3).

Implementation
--------------

.. autoclass:: BsaFormat
   :show-inheritance:
   :members:

Regression tests
----------------

Read a BSA file
^^^^^^^^^^^^^^^

>>> # check and read bsa file
>>> stream = open('tests/bsa/test.bsa', 'rb')
>>> data = BsaFormat.Data()
>>> data.inspect_quick(stream)
>>> data.version
103
>>> data.inspect(stream)
>>> data.offset
36
>>> data.flags
>>> data.num_folders
>>> data.num_files
>>> data.read(stream)
>>> # TODO check something else...

Parse all BSA files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in BsaFormat.walkData('tests/bsa'):
...     print(stream.name)
tests/bsa/test.bsa

Create an BSA file from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> data = BsaFormat.Data()
>>> # TODO store something...
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

from itertools import izip
import struct
import os
import re

import pyffi.object_models.xml
import pyffi.object_models.common
from pyffi.object_models.xml.basic import BasicBase
import pyffi.object_models
from pyffi.utils.graph import EdgeFilter

class BsaFormat(pyffi.object_models.xml.FileFormat):
    """This class implements the BSA format."""
    xml_file_name = 'bsa.xml'
    # where to look for bsa.xml and in what order:
    # BSAXMLPATH env var, or BsaFormat module directory
    xml_file_path = [os.getenv('BSAXMLPATH'), os.path.dirname(__file__)]
    # file name regular expression match
    RE_FILENAME = re.compile(r'^.*\.bsa$', re.IGNORECASE)

    # basic types
    UInt32 = pyffi.object_models.common.UInt
    UInt64 = pyffi.object_models.common.UInt64
    ZString = pyffi.object_models.common.ZString

    # implementation of bsa-specific basic types

    class FileSignature(BasicBase):
        """Basic type which implements the header of a BSA file."""
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)

        def __str__(self):
            return 'BSA'

        def get_detail_display(self):
            return self.__str__()

        def get_hash(self, **kwargs):
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
            if hdrstr != "BSA\x00".encode("ascii"):
                raise ValueError(
                    "invalid BSA header: expected 'BSA\\x00' but got '%s'"
                    % hdrstr)

        def write(self, stream, **kwargs):
            """Write the header string to stream.

            :param stream: The stream to write to.
            :type stream: file
            """
            stream.write("BSA\x00".encode("ascii"))

        def get_size(self, **kwargs):
            """Return number of bytes the header string occupies in a file.

            :return: Number of bytes.
            """
            return 4

    @staticmethod
    def version_number(version_str):
        """Converts version string into an integer.

        :param version_str: The version string.
        :type version_str: str
        :return: A version integer.

        >>> BsaFormat.version_number('103')
        103
        >>> BsaFormat.version_number('XXX')
        -1
        """
        try:
            return int(version_str)
        except ValueError:
            # not supported
            return -1

    class Header(pyffi.object_models.FileFormat.Data):
        """A class to contain the actual bsa data."""
        user_version = None # not used

        def inspect_quick(self, stream):
            """Quickly checks if stream contains BSA data, and gets the
            version, by looking at the first 8 bytes.

            :param stream: The stream to inspect.
            :type stream: file
            """
            pos = stream.tell()
            try:
                self._signature_value_.read(stream)
                self._version_value_.read(stream)
            finally:
                stream.seek(pos)

        # overriding pyffi.object_models.FileFormat.Data methods

        def inspect(self, stream):
            """Quickly checks if stream contains BSA data, and reads the
            header.

            :param stream: The stream to inspect.
            :type stream: file
            """
            pos = stream.tell()
            try:
                self.inspect_quick(stream)
                BsaFormat._Header.read(self, stream, data=self)
            finally:
                stream.seek(pos)

        def read(self, stream):
            """Read a bsa file.

            :param stream: The stream from which to read.
            :type stream: ``file``
            """
            # read the file
            self.inspect(stream)
            self.folders.read(stream, data=self)

            # check if we are at the end of the file
            #if stream.read(1):
            #    raise ValueError(
            #        'end of file not reached: corrupt bsa file?')
            
        def write(self, stream):
            """Write a bsa file.

            :param stream: The stream to which to write.
            :type stream: ``file``
            """
            # write the file
            raise NotImplementedError

if __name__=='__main__':
    import doctest
    doctest.testmod()
