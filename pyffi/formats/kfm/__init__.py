"""
:mod:`pyffi.formats.kfm` --- NetImmerse/Gamebryo Keyframe Motion (.kfm)
=======================================================================

Regression tests
----------------

Read a KFM file
^^^^^^^^^^^^^^^

>>> # read kfm file
>>> stream = open('tests/kfm/test.kfm', 'rb')
>>> data = KfmFormat.Data()
>>> data.inspect(stream)
>>> print(data.nifFileName)
Test.nif
>>> data.read(stream)
>>> stream.close()
>>> # get all animation file names
>>> for anim in data.animations:
...     print(anim.kfFileName)
Test_MD_Idle.kf
Test_MD_Run.kf
Test_MD_Walk.kf
Test_MD_Die.kf

Parse all KFM files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in KfmFormat.walkData('tests/kfm'):
...     print stream.name
tests/kfm/test.kfm

Create a KFM model from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> data = KfmFormat.Data()
>>> data.nifFileName = "Test.nif"
>>> data.numAnimations = 4
>>> data.animations.updateSize()
>>> data.animations[0].kfFileName = "Test_MD_Idle.kf"
>>> data.animations[1].kfFileName = "Test_MD_Run.kf"
>>> data.animations[2].kfFileName = "Test_MD_Walk.kf"
>>> data.animations[3].kfFileName = "Test_MD_Die.kf"
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> data.write(stream)
>>> stream.close()

Get list of versions and games
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for vnum in sorted(KfmFormat.versions.values()):
...     print('0x%08X' % vnum)
0x01000000
0x01024B00
0x0200000B
0x0201000B
0x0202000B
>>> for game, versions in sorted(KfmFormat.games.items(),
...                              key=lambda x: x[0]):
...     print("%s " % game + " ".join('0x%08X' % vnum for vnum in versions))
Civilization IV 0x01000000 0x01024B00 0x0200000B
Emerge 0x0201000B 0x0202000B
Loki 0x01024B00
Megami Tensei: Imagine 0x0201000B
Oblivion 0x01024B00
Prison Tycoon 0x01024B00
Pro Cycling Manager 0x01024B00
Red Ocean 0x01024B00
Sid Meier's Railroads 0x0200000B
The Guild 2 0x01024B00
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, NIF File Format Library and Tools.
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
#    * Neither the name of the NIF File Format Library and Tools
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

import pyffi.object_models.xml
from pyffi.object_models import Common
from pyffi.object_models.xml.Basic import BasicBase
from pyffi.utils.graph import EdgeFilter
import pyffi.object_models
import pyffi.object_models.xml.Struct

class KfmFormat(pyffi.object_models.xml.FileFormat):
    """This class implements the kfm file format."""
    xmlFileName = 'kfm.xml'
    # where to look for kfm.xml and in what order:
    # KFMXMLPATH env var, or KfmFormat module directory
    xmlFilePath = [os.getenv('KFMXMLPATH'), os.path.dirname(__file__)]
    # file name regular expression match
    RE_FILENAME = re.compile(r'^.*\.kfm$', re.IGNORECASE)
    # used for comparing floats
    _EPSILON = 0.0001

    # basic types
    int = Common.Int
    uint = Common.UInt
    byte = Common.UByte # not a typo
    char = Common.Char
    short = Common.Short
    ushort = Common.UShort
    float = Common.Float
    SizedString = Common.SizedString
    TextString = Common.UndecodedData # for text (used by older kfm versions)

    # implementation of kfm-specific basic types

    class HeaderString(BasicBase):
        """The kfm header string."""
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)
            self._doseol = False

        def __str__(self):
            return ';Gamebryo KFM File Version x.x.x.x'

        def getHash(self, **kwargs):
            """Return a hash value for this value.

            :return: An immutable object that can be used as a hash.
            """
            return None

        def read(self, stream, **kwargs):
            """Read header string from stream and check it.

            :param stream: The stream to read from.
            :type stream: file
            :keyword version: The file version.
            :type version: int
            """
            # get the string we expect
            version_string = self.versionString(kwargs.get('version'))
            # read string from stream
            hdrstr = stream.read(len(version_string))
            # check if the string is correct
            if hdrstr != version_string:
                raise ValueError(
                    "invalid KFM header: expected '%s' but got '%s'"
                    % (version_string, hdrstr))
            # check eol style
            nextchar = stream.read(1)
            if nextchar == '\x0d':
                nextchar = stream.read(1)
                self._doseol = True
            else:
                self._doseol = False
            if nextchar != '\x0a':
                raise ValueError(
                    "invalid KFM header: string does not end on \\n or \\r\\n")

        def write(self, stream, **kwargs):
            """Write the header string to stream.

            :param stream: The stream to write to.
            :type stream: file
            """
            # write the version string
            stream.write(self.versionString(kwargs.get('version')))
            # write \n (or \r\n for older versions)
            if self._doseol:
                stream.write('\x0d\x0a')
            else:
                stream.write('\x0a')

        def getSize(self, **kwargs):
            """Return number of bytes the header string occupies in a file.

            :return: Number of bytes.
            """
            return len(self.versionString(kwargs.get('version'))) \
                   + (1 if not self._doseol else 2)

        # DetailNode

        def getDetailDisplay(self):
            return str(self)

        @staticmethod
        def versionString(version):
            """Transforms version number into a version string.

            :param version: The version number.
            :type version: int
            :return: A version string.

            >>> KfmFormat.HeaderString.versionString(0x0202000b)
            ';Gamebryo KFM File Version 2.2.0.0b'
            >>> KfmFormat.HeaderString.versionString(0x01024b00)
            ';Gamebryo KFM File Version 1.2.4b'
            """
            if version == -1 or version is None:
                raise RuntimeError('no string for version %s'%version)
            return ";Gamebryo KFM File Version %s"%({
                0x01000000 : "1.0",
                0x01024b00 : "1.2.4b",
                0x0200000b : "2.0.0.0b",
                0x0201000b : "2.1.0.0b",
                0x0202000b : "2.2.0.0b" } [version])

    # other types with internal implementation
    class FilePath(SizedString):
        def getHash(self, **kwargs):
            """Return a hash value for this value.
            For file paths, the hash value is case insensitive.

            :return: An immutable object that can be used as a hash.
            """
            return self.getValue().lower()

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        :param version_str: The version string.
        :type version_str: str
        :return: A version integer.

        >>> hex(KfmFormat.versionNumber('1.0'))
        '0x1000000'
        >>> hex(KfmFormat.versionNumber('1.2.4b'))
        '0x1024b00'
        >>> hex(KfmFormat.versionNumber('2.2.0.0b'))
        '0x202000b'
        """

        if not '.' in version_str:
            return int(version_str)

        try:
            ver_list = [int(x, 16) for x in version_str.split('.')]
        except ValueError:
            # version not supported (i.e. version_str '10.0.1.3z' would
            # trigger this)
            return -1
        if len(ver_list) > 4 or len(ver_list) < 1:
            # version not supported
            return -1
        for ver_digit in ver_list:
            if (ver_digit | 0xff) > 0xff:
                return -1 # version not supported
        while len(ver_list) < 4:
            ver_list.append(0)
        return ((ver_list[0] << 24)
                + (ver_list[1] << 16)
                + (ver_list[2] << 8)
                + ver_list[3])

    class Header(pyffi.object_models.FileFormat.Data):
        """A class to contain the actual kfm data."""
        version = 0x01024B00

        def inspect(self, stream):
            """Quick heuristic check if stream contains KFM data,
            by looking at the first 64 bytes. Sets version and reads
            header string.

            :param stream: The stream to inspect.
            :type stream: file
            """
            pos = stream.tell()
            try:
                hdrstr = stream.readline(64).rstrip()
            finally:
                stream.seek(pos)
            if hdrstr.startswith(";Gamebryo KFM File Version "):
                version_str = hdrstr[27:]
            else:
                # not a kfm file
                raise ValueError("Not a KFM file.")
            try:
                ver = KfmFormat.versionNumber(version_str)
            except:
                # version not supported
                raise ValueError("KFM version not supported.")
            if not ver in KfmFormat.versions.values():
                # unsupported version
                raise ValueError("KFM version not supported.")
            # store version
            self.version = ver
            # read header string
            try:
                self._headerString_value_.read(stream, version=ver)
                self._unknownByte_value_.read(stream, version=ver)
                self._nifFileName_value_.read(stream, version=ver)
                self._master_value_.read(stream, version=ver)
            finally:
                stream.seek(pos)

        def read(self, stream):
            """Read a kfm file.

            :param stream: The stream from which to read.
            :type stream: ``file``
            """
            # read the file
            self.inspect(stream) # quick check
            pyffi.object_models.xml.Struct.StructBase.read(
                self, stream, version=self.version)

            # check if we are at the end of the file
            if stream.read(1) != '':
                raise ValueError('end of file not reached: corrupt kfm file?')

        def write(self, stream):
            """Write a kfm file.

            :param stream: The stream to which to write.
            :type stream: ``file``
            """
            # write the file
            pyffi.object_models.xml.Struct.StructBase.write(
                self, stream, version=self.version)

        # GlobalNode

        def getGlobalChildNodes(self, edge_filter=EdgeFilter()):
            return (anim for anim in self.animations)

        def getGlobalDisplay(self):
            """Display the nif file name."""
            return self.nifFileName

    class Animation:
        # XXX this does not work yet (see todo for KfmFormat)
        def getDetailDisplay(self):
            """Display the kf file name."""
            return self.kfFileName if not self.name else self.name

        def getGlobalDisplay(self):
            """Display the kf file name."""
            return self.kfFileName if not self.name else self.name
