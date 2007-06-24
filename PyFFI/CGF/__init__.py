# --------------------------------------------------------------------------
# PyFFI.CGF
# Implementation of the CGF file format.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, Python File Format Interface
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
# --------------------------------------------------------------------------

import struct, os, re

from PyFFI import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI import Common

class CgfFormat(object):
    """Stores all information about the cgf file format."""
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'cgf.xml'
    xmlFilePath = [ os.getenv('CGFXMLPATH'), os.path.dirname(__file__) ] # where to look for cgf.xml and in what order: CGFXMLPATH env var, or module directory
    clsFilePath = os.path.dirname(__file__) # path of class customizers
    _EPSILON = 0.0001 # used for comparing floats
    
    # basic types
    int = Common.Int
    uint = Common.UInt
    byte = Common.Byte
    ubyte = Common.UByte
    short = Common.Short
    ushort = Common.UShort
    char = Common.Char
    float = Common.Float

    # exceptions
    class CgfError(StandardError):
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        >>> hex(CgfFormat.versionNumber('744'))
        '0x744'
        """
        return int(version_str, 16)

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable
        by Python.

        >>> CgfFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """
        
        parts = str(name).split() # str(name) converts name to string in case name is a unicode string
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    @classmethod
    def getVersion(cls, f):
        """Returns file type (geometry or animation) and version of the
        chunk table.

        Returns -1, 0 if file type or chunk table version is not supported.
        Returns -2, 0 if <f> is not a cgf file.
        """
        pos = f.tell()
        try:
            s = f.read(7)
            filetype, fileversion = struct.unpack('<II', f.read(8))
        except StandardError:
            return -2, 0
        finally:
            f.seek(pos)
        if s != "CryTek\x00":
            return -2, 0
        if filetype not in [ cls.FileType.GEOM, cls.FileType.ANIM ]:
            return -1, 0
        if fileversion not in cls.ChunkTable.versions.keys():
            return -1, 0
        return filetype, fileversion

    @classmethod
    def read(cls, version, f, verbose = 0):
		raise NotImplementedError

    @classmethod
    def write(cls, version, f, chunks, verbose = 0):
		raise NotImplementedError
