"""Format classes and metaclasses for binary file formats described by a
mexscript file, and mexscript parser for converting the mexscript description
into Python classes.
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

import logging

import PyFFI.ObjectModels.FileFormat

class MexScriptFileFormat(PyFFI.ObjectModels.FileFormat.FileFormat):
    """This class can be used as a base class for file formats
    described by a mexscript file."""
    mexscript_filename = None #: Override.
    mexscript_filepath = None #: Override.

    class Blob(PyFFI.ObjectModels.SimpleType):
        """An uncompressed blob of data."""

        fileformat = None
        """If the file has a specific format, it is described here by a
        `PyFFI.ObjectModels.FileFormat.FileFormat` class.
        """

        def __init__(self):
            self._value = "" # py3k: bytes object

        def __str__(self):
            return "<BLOB>"

        def read(self, stream, context):
            """Read the blob. The lenght is passed as an argument."""
            self._value = stream.read(context.length)

        def write(self, stream, context):
            """Write the blob."""
            self.write(self._value)

    class FileInfo:
        """Stores information about a file in an archive."""
        filename = ""
        """Name of the file."""
        
        offset = None
        """Offset in the archive."""

        size = None
        """Compressed size in the archive."""

        uncompressed_size = None
        """Uncompressed size in the archive."""

        offset_offset = None
        """Offset of the offset of this file in the archive."""

        offset_size = None
        """Offset of the size of this file in the archive."""

        offset_uncompressed_size = None
        """Offset of the uncompressed size in the archive."""

    class Data(PyFFI.ObjectModels.FileFormat.FileFormat.Data):
        """Process archives described by mexscript files.
        The interface is similar to that of :class:`TarFile`.
        """

        _fileinfos = []
        """List of file info's in the data."""

        def read(self, stream):
            """Open and read a full archive from stream while parsing the
            mexscript. The files in the archive are not decoded.

            If you want to open the archive without processing the
            full list of files, use :meth:`open`.

            :param stream: The archive to read from.
            :type stream: file
            """
            raise NotImplementedError
