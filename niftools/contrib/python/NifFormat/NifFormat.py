# --------------------------------------------------------------------------
# NifFormat.NifFormat
# Implementation of the NIF file format; uses FileFormat.XmlFileFormat.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, NIF File Format Library and Tools.
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
# --------------------------------------------------------------------------

import struct
from FileFormat.XmlFileFormat import MetaXmlFileFormat
from BasicTypes import *

class NifError(Exception):
    pass

class NifFormat(object):
    """Stores all information about the nif file format.
    
    >>> for vnum in sorted(NifFormat.versions.values()): print '0x%08X'%vnum
    0x03010000
    0x0303000D
    0x04000000
    0x04000002
    0x0401000C
    0x04020002
    0x04020100
    0x04020200
    0x0A000100
    0x0A000102
    0x0A010000
    0x0A01006A
    0x0A020000
    0x14000004
    0x14000005
    >>> print NifFormat.HeaderString
    <class 'NifFormat.BasicTypes.HeaderString'>
    """
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'nif.xml'
    xmlFilePath = [ '.', '../../docsys' ]
    basicClasses = {
        'int'    : Int,
        'uint'   : UInt,
        'bool'   : Bool,
        'byte'   : Byte,
        'char'   : Char,
        'short'  : Short,
        'ushort' : UShort,
        'float'  : Float,
        'Ptr'    : Ptr,
        'Ref'    : Ref,
        'BlockTypeIndex' : UShort,
        'StringOffset' : UInt,
        'FileVersion' : FileVersion,
        'Flags' : Flags,
        'HeaderString' : HeaderString,
        'LineString' : LineString }

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        >>> hex(NifFormat.versionNumber('3.14.15.29'))
        '0x30e0f1d'
        >>> hex(NifFormat.versionNumber('1.2'))
        '0x1020000'
        """
        
        v = version_str.split('.')
        num = 0
        shift = 24
        for x in v:
            num += int(x) << shift
            shift -= 8
        return num

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable by python.

        >>> NifFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """
        
        parts = str(name).split() # str(name) converts name to string in case name is a unicode string
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    @classmethod
    def getVersion(cls, f):
        """Returns version number, if version is supported.
        Returns -1 if version is not supported.
        Returns -2 if <f> is not a nif file.
        """
        pos = f.tell()
        try:
            s = f.readline(64).rstrip()
        finally:
            f.seek(pos)
        if s.startswith("NetImmerse File Format, Version " ):
            ver_str = s[32:]
        elif s.startswith("Gamebryo File Format, Version "):
            ver_str = s[30:]
        else:
            return -2 # not a nif file
        try:
            ver_list = [int(x) for x in ver_str.split('.')]
        except ValueError:
            return -1 # version not supported (i.e. ver_str '10.0.1.3a' would trigger this)
        if len(ver_list) > 4 or len(ver_list) < 1:
            return -1 # version not supported
        for ver_digit in ver_list:
            if (ver_digit | 0xff) > 0xff:
                return -1 # version not supported
        while len(ver_list) < 4: ver_list.append(0)
        ver = ver_list[0] << 24 + ver_list[1] << 16 + ver_list[2] << 8 + ver_list[3]
        if not ver in cls.values():
            return -1 # unsupported version
        # check version integer
        if ver >= 0x0303000D:
            try:
                f.readline(64)
                ver_int = struct.unpack('<I', f.read(4))
            finally:
                f.seek(pos)
            if ver_int != ver:
                return -2 # not a nif file
        return ver

    @classmethod
    def read(cls, f, version, user_version):
        # read header
        hdr = cls.Header()
        hdr.read(f, version, user_version)
        
        # read the blocks
        block_dct = {} # maps block index to actual block
        block_indices = [] # records all indices as read from the nif file in the proper order
        block_list = [] # records all blocks as read from the nif file in the proper order
        link_stack = [] # list of indices, as they are added to the stack
        block_num = 0 # the current block numner

        while True:
            # get block name
            if version >= 0x05000001:
                if version <= 0x0A01006A:
                    dummy = struct.unpack('<I', f.read(4))
                    if dummy != 0:
                        raise NifError('NIF read: invalid block position (expected 0x00000000 but got 0x%08X at 0x%08X)'%(dummy, f.tell()))
                block_type = hdr.blockTypes[header.blockTypeIndex[block_num]]
            else:
                block_type = cls.String()
                block_type.read(f, version, user_version)
            if version < 0x0303000D:
                if block_type == "Top Level Object": continue
                if block_type == "End Of File": break
            # create block
            block = getattr(cls, str(block_type))()
            print block_type
            # get the block index
            if version < 0x0303000D:
                block_index = struct.unpack('<I', f.read(4))
                if block_index in block_indices:
                    raise NifError('NIF read: duplicate block index (0x%08X at 0x%08X)'%(block_index, f.tell()))
            else:
                block_index = block_num
            block_indices.append(block_index)
            block.read(f, link_stack, version, user_version)
            block_dct[block_index] = block
            block_list.append(block)
            # check if we are done
            if version >= 0x0303000D:
                block_num += 1
                if block_num >= hdr.numBlocks: break

        # read footer
        ftr = cls.Footer()
        ftr.read(f, version, user_version)

        # fix links
        for block_index in block_indices:
            block_dct[block_index].fixLinks(block_list, link_stack, version, user_version)

        # return root objects
        roots = []
        for root in ftr.roots:
            roots.append(root)
        return roots

    @classmethod
    def write(cls, roots, f, version, user_version):
        # TODO set up link stack
        #blk_num = {}
        #blk_num[root] = 0

        # set up header
        hdr = cls.Header()
        hdr.userVersion = user_version # TODO dedicated type for userVersion similar to FileVersion

        # set up footer
        ftr = cls.Footer()
        ftr.numRoots = len(roots)
        ftr.roots.updateSize()
        for i, root in enumerate(roots):
            ftr.roots[i] = root

        # write the file
        hdr.write(f, version, user_version)
        # TODO write the actual blocks
        ftr.write(f, version, user_version)
