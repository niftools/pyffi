"""
This module implements the KFM file format.

Examples
========

Read a KFM file
---------------

>>> # get version and user version, and read kfm file
>>> f = open('test.kfm', 'rb')
>>> version = KfmFormat.getVersion(f)
>>> if version == -1:
...     raise RuntimeError('kfm version not supported')
... elif version == -2:
...     raise RuntimeError('not a kfm file')
>>> header, animations, footer = KfmFormat.read(f, version = version)
>>> # print all animation file names
>>> print header.nifFileName
Test.nif
>>> for anim in animations:
...     print anim.kfFileName
Test_MD_Idle.kf
Test_MD_Run.kf
Test_MD_Walk.kf
Test_MD_Die.kf

Create a KFM model from scratch and write to file
-------------------------------------------------

>>> header = KfmFormat.Header()
>>> header.nifFileName = "Test.nif"
>>> header.numAnimations = 4
>>> animations = [ KfmFormat.Animation() for j in xrange(4) ]
>>> animations[0].kfFileName = "Test_MD_Idle.kf"
>>> animations[1].kfFileName = "Test_MD_Run.kf"
>>> animations[2].kfFileName = "Test_MD_Walk.kf"
>>> animations[3].kfFileName = "Test_MD_Die.kf"
>>> from tempfile import TemporaryFile
>>> f = TemporaryFile()
>>> KfmFormat.write(f, version = 0x0202000B, header = header, animations = animations)

Get list of versions and games
------------------------------

>>> for vnum in sorted(KfmFormat.versions.values()): print '0x%08X'%vnum
0x01000000
0x01024B00
0x0200000B
0x0201000B
0x0202000B
>>> for game, versions in sorted(KfmFormat.games.items(), key=lambda x: x[0]):
...     print game,
...     for vnum in versions:
...         print '0x%08X'%vnum,
...     print
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
# Copyright (c) 2007-2008, NIF File Format Library and Tools.
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
# ***** END LICENCE BLOCK *****

import struct, os, re

from PyFFI import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI import Common
from PyFFI.Bases.Basic import BasicBase

class KfmFormat(object):
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'kfm.xml'
    # where to look for kfm.xml and in what order:
    # KFMXMLPATH env var, or KfmFormat module directory
    xmlFilePath = [ os.getenv('KFMXMLPATH'), os.path.dirname(__file__) ]
    # path of class customizers
    clsFilePath = os.path.dirname(__file__)
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

    # implementation of kfm-specific basic types

    class HeaderString(BasicBase):
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)            
            self._doseol = False

        def __str__(self):
            return ';Gamebryo KFM File Version x.x.x.x'

        def getHash(self, **kwargs):
            return None

        def read(self, stream, **kwargs):
            # get the string we expect
            version_string = self.versionString(kwargs.get('version'))
            # read string from stream
            s = stream.read(len(version_string))
            # check if the string is correct
            if s != version_string:
                raise ValueError(
                    "invalid KFM header: expected '%s' but got '%s'"
                    % (version_string, s))
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
            # write the version string
            stream.write(self.versionString(kwargs.get('version')))
            # write \n (or \r\n for older versions)
            if self._doseol:
                stream.write('\x0d\x0a')
            else:
                stream.write('\x0a')

        def getSize(self, **kwargs):
            return len(self.versionString(kwargs.get('version'))) \
                   + (1 if not self._doseol else 2)

        @staticmethod
        def versionString(version):
            """Transforms version number into a version string.

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

    class SizedString(BasicBase):
        """Basic type for strings.

        >>> from tempfile import TemporaryFile
        >>> f = TemporaryFile()
        >>> s = KfmFormat.SizedString()
        >>> f.write('\\x07\\x00\\x00\\x00abcdefg')
        >>> f.seek(0)
        >>> s.read(f)
        >>> str(s)
        'abcdefg'
        >>> f.seek(0)
        >>> s.setValue('Hi There')
        >>> s.write(f)
        >>> f.seek(0)
        >>> m = KfmFormat.SizedString()
        >>> m.read(f)
        >>> str(m)
        'Hi There'
        """
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)            
            self.setValue('')

        def getValue(self):
            return self._value

        def setValue(self, value):
            if len(value) > 10000: raise ValueError('string too long')
            self._value = str(value)

        def __str__(self):
            s = self._value
            if not s: return '<EMPTY STRING>'
            return s

        def getSize(self, **kwargs):
            return 4+len(self._value)

        def getHash(self, **kwargs):
            return self.getValue()

        def read(self, stream, **kwargs):
            n, = struct.unpack('<I', stream.read(4))
            if n > 10000: raise ValueError('string too long (0x%08X at 0x%08X)'%(n, stream.tell()))
            self._value = stream.read(n)

        def write(self, stream, **kwargs):
            stream.write(struct.pack('<I', len(self._value)))
            stream.write(self._value)

    class TextString(BasicBase):
        """Basic type for text (used by older kfm versions).

        >>> from tempfile import TemporaryFile
        >>> f = TemporaryFile()
        >>> s = KfmFormat.TextString()
        >>> f.write('abcdefg')
        >>> f.seek(0)
        >>> s.read(f)
        >>> str(s)
        'abcdefg'
        >>> f.seek(0)
        >>> s.setValue('Hi There Everybody')
        >>> s.write(f)
        >>> f.seek(0)
        >>> m = KfmFormat.TextString()
        >>> m.read(f)
        >>> str(m)
        'Hi There Everybody'
        """
        def __init__(self, **kwargs):
            BasicBase.__init__(self, **kwargs)            
            self.setValue('')

        def getValue(self):
            return self._value

        def setValue(self, value):
            if len(value) > 10000:
                raise ValueError('text too long')
            self._value = str(value)

        def __str__(self):
            s = self._value
            if not s:
                return '<EMPTY TEXT>'
            return s

        def getSize(self, **kwargs):
            return len(self._value)

        def getHash(self, **kwargs):
            return self.getValue()

        def read(self, stream, **kwargs):
            self._value = stream.read(-1)

        def write(self, stream, **kwargs):
            stream.write(self._value)

    # other types with internal implementation
    class FilePath(SizedString):
        def getHash(self, **kwargs):
            # never ignore file paths
            # transform to lower case to make hash case insensitive
            return self.getValue().lower()

    # exceptions
    class KfmError(StandardError):
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

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
        return (ver_list[0] << 24) + (ver_list[1] << 16) + (ver_list[2] << 8) + ver_list[3]

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable
        by python.

        >>> KfmFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """
        
        # str(name) converts name to string in case name is a unicode string
        parts = str(name).replace("?", "X").split()
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    @classmethod
    def getVersion(cls, stream):
        """Returns version and user version number, if version is supported.

        @param stream: The stream from which to read, typically a file or a
            memory stream such as cStringIO.
        @return: The version and user version of the file.
            Returns -1 if a kfm file but version not supported.
            Returns -2 if not a kfm file.
        """
        pos = stream.tell()
        try:
            s = stream.readline(64).rstrip()
        finally:
            stream.seek(pos)
        if s.startswith(";Gamebryo KFM File Version " ):
            version_str = s[27:]
        else:
            # not a kfm file
            return -2
        try:
            ver = cls.versionNumber(version_str)
        except:
            # version not supported
            return -1
        if not ver in cls.versions.values():
            # unsupported version
            return -1

        return ver

    @classmethod
    def read(cls, stream, version = None,
             verbose = 0):
        """Read a kfm file.

        @param stream: The stream from which to read, typically a file or a
            memory stream such as cStringIO.
        @param version: The version number as obtained by getVersion.
        @param user_version: The user version number as obtained by getVersion.
        @param verbose: The level of verbosity."""
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
    def write(cls, stream, version = None,
              header = None, animations = None, footer = None, verbose = 0):
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

    @classmethod
    def walk(cls, top, topdown = True, onerror = None, verbose = 0):
        """A generator which yields the roots of all files in directory top
        whose filename matches the regular expression re_filename. The argument
        top can also be a file instead of a directory. The argument onerror,
        if set, will be called if cls.read raises an exception (errors coming
        from os.walk will be ignored)."""
        for version, f, kfm in cls.walkFile(top, topdown, onerror, verbose):
            yield kfm

    @classmethod
    def walkFile(cls, top, topdown = True,
                 raisereaderror = False, verbose = 0, mode = 'rb'):
        """Like walk, but returns more information:
        version, f, and kfm.

        Note that the caller is not responsible for closing stream.

        walkFile is for instance used by runtest.py to implement the
        testFile-style tests which must access the file after the file has been
        read."""
        # filter for recognizing kfm files by extension
        re_kfm = re.compile(r'^.*\.kfm$', re.IGNORECASE)
        # now walk over all these files in directory top
        for filename in Utils.walk(top, topdown, onerror = None,
                                   re_filename = re_kfm):
            if verbose >= 1: print "reading %s"%filename
            stream = open(filename, mode)
            try:
                # get the version
                version = cls.getVersion(stream)
                if version >= 0:
                    # we got it, so now read the kfm file
                    if verbose >= 2: print "version 0x%08X"%version
                    try:
                        # return (version, stream, (header, animations, footer))
                        yield (version, stream,
                               cls.read(stream, version = version))
                    except StandardError:
                        # an error occurred during reading
                        # this should not happen: means that the file is
                        # corrupt, or that the xml is corrupt
                        if verbose >= 1:
                            print """
Warning: read failed due to either a corrupt kfm file, a corrupt kfm.xml,
or a bug in KfmFormat library."""
                        if verbose >= 2:
                            Utils.hexDump(stream)
                        if raisereaderror:
                            raise
                # getting version failed, do not raise an exception
                # but tell user what happened
                elif version == -1:
                    if verbose >= 1: print 'version not supported'
                else:
                    if verbose >= 1: print 'not a kfm file'
            finally:
                stream.close()
