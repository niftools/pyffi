"""
.. :mod:`PyFFI.Formats.KFM` --- NetImmerse/Gamebryo Keyframe Motion (.kfm)
   =======================================================================

Regression tests
----------------

Read a KFM file
^^^^^^^^^^^^^^^

>>> # get version and user version, and read kfm file
>>> f = open('tests/kfm/test.kfm', 'rb')
>>> version, user_version = KfmFormat.getVersion(f)
>>> if version == -1:
...     raise RuntimeError('kfm version not supported')
... elif version == -2:
...     raise RuntimeError('not a kfm file')
>>> header, animations, footer = KfmFormat.read(f, version = version)
>>> # get all animation file names
>>> print(header.nifFileName)
Test.nif
>>> for anim in animations:
...     print(anim.kfFileName)
Test_MD_Idle.kf
Test_MD_Run.kf
Test_MD_Walk.kf
Test_MD_Die.kf

Parse all KFM files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for header, animations, footer in KfmFormat.walk('tests/kfm',
...                                                  raisereaderror = False,
...                                                  verbose = 1):
...     pass
reading tests/kfm/test.kfm

Create a KFM model from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> header = KfmFormat.Header()
>>> header.nifFileName = "Test.nif"
>>> header.numAnimations = 4
>>> animations = [KfmFormat.Animation() for j in xrange(4)]
>>> animations[0].kfFileName = "Test_MD_Idle.kf"
>>> animations[1].kfFileName = "Test_MD_Run.kf"
>>> animations[2].kfFileName = "Test_MD_Walk.kf"
>>> animations[3].kfFileName = "Test_MD_Die.kf"
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> KfmFormat.write(stream, version = 0x0202000B,
...                 header = header, animations = animations)

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

from PyFFI.ObjectModels.XML.FileFormat import XmlFileFormat
from PyFFI.ObjectModels.XML.FileFormat import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI.ObjectModels import Common
from PyFFI.ObjectModels.XML.Basic import BasicBase

class KfmFormat(XmlFileFormat):
    """This class implements the kfm file format."""
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'kfm.xml'
    # where to look for kfm.xml and in what order:
    # KFMXMLPATH env var, or KfmFormat module directory
    xmlFilePath = [os.getenv('KFMXMLPATH'), os.path.dirname(__file__)]
    # path of class customizers
    clsFilePath = os.path.dirname(__file__)
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

            @return: An immutable object that can be used as a hash.
            """
            return None

        def read(self, stream, **kwargs):
            """Read header string from stream and check it.

            @param stream: The stream to read from.
            @type stream: file
            @keyword version: The file version.
            @type version: int
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

            @param stream: The stream to write to.
            @type stream: file
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

            @return: Number of bytes.
            """
            return len(self.versionString(kwargs.get('version'))) \
                   + (1 if not self._doseol else 2)

        @staticmethod
        def versionString(version):
            """Transforms version number into a version string.

            @param version: The version number.
            @type version: int
            @return: A version string.

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

            @return: An immutable object that can be used as a hash.
            """
            return self.getValue().lower()

    # exceptions
    class KfmError(StandardError):
        """Exception class used for KFM related exceptions."""
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        @param version_str: The version string.
        @type version_str: str
        @return: A version integer.

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

    @classmethod
    def getVersion(cls, stream):
        """Returns version and user version number, if version is supported.

        @param stream: The stream from which to read.
        @type stream: file
        @return: The version and user version of the file.
            Returns C{(-1, 0)} if a kfm file but version not supported.
            Returns C{(-2, 0)} if not a kfm file.
        """
        pos = stream.tell()
        try:
            hdrstr = stream.readline(64).rstrip()
        finally:
            stream.seek(pos)
        if hdrstr.startswith(";Gamebryo KFM File Version " ):
            version_str = hdrstr[27:]
        else:
            # not a kfm file
            return -2, 0
        try:
            ver = cls.versionNumber(version_str)
        except:
            # version not supported
            return -1, 0
        if not ver in cls.versions.values():
            # unsupported version
            return -1, 0

        return ver, 0

    @classmethod
    def read(cls, stream, version = None, user_version = None, verbose = 0):
        """Read a kfm file.

        @param stream: The stream from which to read.
        @type stream: file
        @param version: The kfm version obtained by L{getVersion}.
        @type version: int
        @param user_version: The kfm user version obtained by L{getVersion}.
        @type user_version: int
        @param verbose: The level of verbosity.
        @type verbose: int
        @return: header, list of animations, footer
        """
        # read the file
        header = cls.Header()
        header.read(stream, version = version)
        animations = [ cls.Animation() for i in xrange(header.numAnimations) ]
        for anim in animations:
            anim.read(stream, version = version)
        footer = cls.Footer()
        footer.read(stream, version = version)

        # check if we are at the end of the file
        if stream.read(1) != '':
            raise cls.KfmError('end of file not reached: corrupt kfm file?')

        return header, animations, footer

    @classmethod
    def write(cls, stream, version = None, user_version = None,
              header = None, animations = None, footer = None,
              verbose = 0):
        """Write a kfm file.

        @param stream: The stream to which to write.
        @type stream: file
        @param version: The version number.
        @type version: int
        @param user_version: The user version number (ignored for now).
        @type user_version: int
        @param header: The kfm header.
        @type header: L{KfmFormat.Header}
        @param animations: The animation data.
        @type animations: list of L{KfmFormat.Animation}
        @param footer: The kfm footer.
        @type footer: L{KfmFormat.Footer}
        @param verbose: The level of verbosity.
        @type verbose: int
        """
        # make sure header has correct number of animations
        header.numAnimations = len(animations)
        # write the file
        # first header
        assert(isinstance(header, cls.Header))
        header.write(stream, version = version)
        # next all animations
        for anim in animations:
            assert(isinstance(anim, cls.Animation))
            anim.write(stream, version = version)
        # finally the footer
        if footer is None:
            footer = cls.Footer()
        assert(isinstance(footer, cls.Footer))
        footer.write(stream, version = version)
