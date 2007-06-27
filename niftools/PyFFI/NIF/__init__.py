# --------------------------------------------------------------------------
# NifFormat.NifFormat
# Implementation of the NIF file format; uses PyFFI.
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

import struct, os, re

from PyFFI import MetaXmlFileFormat
from PyFFI import Utils
from PyFFI import Common
from PyFFI.Bases.Basic import BasicBase

class NifFormat(object):
    """Stores all information about the nif file format.
    
    >>> for vnum in sorted(NifFormat.versions.values()): print '0x%08X'%vnum
    0x03000000
    0x03000300
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
    >>> for game, versions in sorted(NifFormat.games.items(), key=lambda x: x[0]):
    ...     print game,
    ...     for vnum in versions:
    ...         print '0x%08X'%vnum,
    ...     print
    Axis and Allies 0x0A010000
    Civilization IV 0x04020002 0x04020100 0x04020200 0x0A000100 0x0A010000 0x0A020000 0x14000004
    Dark Age of Camelot 0x03000300 0x03010000 0x0401000C 0x04020100 0x04020200 0x0A010000
    Empire Earth II 0x04020200
    Freedom Force 0x04000000 0x04000002
    Freedom Force vs. the 3rd Reich 0x0A010000
    Kohan 2 0x0A010000
    Morrowind 0x04000002
    Oblivion 0x0303000D 0x0A000102 0x0A01006A 0x0A020000 0x14000004 0x14000005
    Star Trek: Bridge Commander 0x03000000 0x03010000
    Zoo Tycoon 2 0x0A000100
    >>> print NifFormat.HeaderString
    <class 'PyFFI.NIF.HeaderString'>

    Test templates.

    >>> block = NifFormat.NiTextKeyExtraData()
    >>> block.numTextKeys = 1
    >>> block.textKeys.updateSize()
    >>> block.textKeys[0].time = 1.0
    >>> block.textKeys[0].value = 'hi'

    Tests for links.
    
    >>> NifFormat.NiNode._hasLinks
    True
    >>> NifFormat.NiBone._hasLinks
    True

    Tests for mathematics.
    
    >>> m = NifFormat.Matrix44()
    >>> m.setIdentity()
    >>> print m
    [  1.000  0.000  0.000  0.000 ]
    [  0.000  1.000  0.000  0.000 ]
    [  0.000  0.000  1.000  0.000 ]
    [  0.000  0.000  0.000  1.000 ]
    <BLANKLINE>
    >>> s, r, t = m.getScaleRotationTranslation()
    >>> print s
    1.0
    >>> print r
    [  1.000  0.000  0.000 ]
    [  0.000  1.000  0.000 ]
    [  0.000  0.000  1.000 ]
    <BLANKLINE>
    >>> print t
    [  0.000  0.000  0.000 ]
    >>> m.getMatrix33().isScaleRotation()
    True
    >>> m.m21 = 2.0
    >>> m.getMatrix33().isScaleRotation()
    False
    >>> m = NifFormat.Matrix33()
    >>> m.m11 = -0.434308
    >>> m.m12 =  0.893095
    >>> m.m13 = -0.117294
    >>> m.m21 = -0.451770
    >>> m.m22 = -0.103314
    >>> m.m23 =  0.886132
    >>> m.m31 =  0.779282
    >>> m.m32 =  0.437844
    >>> m.m33 =  0.448343
    >>> m == m
    True
    >>> m != m
    False
    >>> print "%.4f"%m.getDeterminant()
    1.0000
    >>> m.isRotation()
    True
    >>> print m.getTranspose()
    [ -0.434 -0.452  0.779 ]
    [  0.893 -0.103  0.438 ]
    [ -0.117  0.886  0.448 ]
    <BLANKLINE>
    >>> m.getInverse() == m.getTranspose()
    True
    >>> m *= 0.321
    >>> print "%.5f"%m.getScale()
    0.32100
    >>> s, r = m.getInverse().getScaleRotation()
    >>> print "%.5f"%s
    3.11526
    >>> abs(0.321 - 1/s) < NifFormat._EPSILON
    True
    >>> print r # same as print m.getTranspose() above
    [ -0.434 -0.452  0.779 ]
    [  0.893 -0.103  0.438 ]
    [ -0.117  0.886  0.448 ]
    <BLANKLINE>
    >>> abs(m.getDeterminant() - 0.321 ** 3) < NifFormat._EPSILON
    True
    >>> m *= -2
    >>> print m
    [  0.279 -0.573  0.075 ]
    [  0.290  0.066 -0.569 ]
    [ -0.500 -0.281 -0.288 ]
    <BLANKLINE>
    >>> print "%.5f"%m.getScale()
    -0.64200
    >>> abs(m.getDeterminant() + 0.642 ** 3) < NifFormat._EPSILON
    True
    >>> n = NifFormat.Matrix44()
    >>> n.setIdentity()
    >>> n.setMatrix33(m)
    >>> t = NifFormat.Vector3()
    >>> t.x = 1.2
    >>> t.y = 3.4
    >>> t.z = 5.6
    >>> n.setTranslation(t)
    >>> print n
    [  0.279 -0.573  0.075  0.000 ]
    [  0.290  0.066 -0.569  0.000 ]
    [ -0.500 -0.281 -0.288  0.000 ]
    [  1.200  3.400  5.600  1.000 ]
    <BLANKLINE>
    >>> n == n
    True
    >>> n != n
    False
    >>> print n.getInverse()
    [  0.676  0.704 -1.214  0.000 ]
    [ -1.391  0.161 -0.682  0.000 ]
    [  0.183 -1.380 -0.698  0.000 ]
    [  2.895  6.338  7.686  1.000 ]
    <BLANKLINE>
    >>> print n.getInverse(fast = False) + 0.000001 # workaround for -0.000
    [  0.676  0.704 -1.214  0.000 ]
    [ -1.391  0.161 -0.682  0.000 ]
    [  0.183 -1.380 -0.698  0.000 ]
    [  2.895  6.338  7.686  1.000 ]
    <BLANKLINE>
    >>> (n * n.getInverse()).isIdentity()
    True
    """
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'nif.xml'
    xmlFilePath = [ os.getenv('NIFXMLPATH'), os.path.dirname(__file__) ] # where to look for nif.xml and in what order: NIFXMLPATH env var, or NifFormat module directory
    clsFilePath = os.path.dirname(__file__) # path of class customizers
    _EPSILON = 0.0001 # used for comparing floats
    
    # basic types
    int = Common.Int
    uint = Common.UInt
    byte = Common.UByte # not a typo
    char = Common.Char
    short = Common.Short
    ushort = Common.UShort
    float = Common.Float
    BlockTypeIndex = Common.UShort
    StringOffset = Common.UInt



    # implementation of nif-specific basic types

    class bool(BasicBase):
        """Basic implementation of a 32-bit (8-bit for versions > 4.0.0.2)
        boolean type.
        
        >>> i = NifFormat.bool()
        >>> i.setValue('false')
        >>> i.getValue()
        False
        >>> i.setValue('true')
        >>> i.getValue()
        True
        """
        def __init__(self, template = None, argument = None):
            self.setValue(False)

        def getValue(self):
            return self._x

        def setValue(self, value):
            if isinstance(value, basestring):
                if value.lower() == 'false':
                    self._x = False
                    return
                elif value == '0':
                    self._x = False
                    return
            if value:
                self._x = True
            else:
                self._x = False

        def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
            if version > 0x04000002:
                value, = struct.unpack('<B', f.read(1))
            else:
                value, = struct.unpack('<I', f.read(4))
            self._x = bool(value)

        def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
            if version > 0x04000002:
                f.write(struct.pack('<B', int(self._x)))
            else:
                f.write(struct.pack('<I', int(self._x)))

    class Flags(Common.UShort):
        def __str__(self):
            return hex(self.getValue())

    class Ref(BasicBase):
        _isTemplate = True
        _hasLinks = True
        _hasRefs = True
        def __init__(self, template = None, argument = None):
            self._template = template
            self.setValue(None)

        def getValue(self):
            return self._x

        def setValue(self, value):
            if value == None:
                self._x = None
            else:
                if not isinstance(value, self._template):
                    raise TypeError('expected an instance of %s but got instance of %s'%(self._template, value.__class__))
                self._x = value

        def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
            self._x = None # fixLinks will set this field
            block_index, = struct.unpack('<i', f.read(4))
            link_stack.append(block_index)

        def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
            if self._x == None: # link by block number
                if version >= 0x0303000D:
                    f.write('\xff\xff\xff\xff') # link by number
                else:
                    f.write('\x00\x00\x00\x00') # link by pointer
            else:
                f.write(struct.pack('<i', block_index_dct[self._x]))

        def fixLinks(self, version, user_version, block_dct, link_stack):
            block_index = link_stack.pop(0)
            # case when there's no link
            if version >= 0x0303000D:
                if block_index == -1: # link by block number
                    self._x = None
                    return
            else:
                if block_index == 0: # link by pointer
                    self._x = None
                    return
            # other case: look up the link and check the link type
            block = block_dct[block_index]
            if not isinstance(block, self._template):
                raise TypeError('expected an instance of %s but got instance of %s'%(self._template, block.__class__))
            self._x = block

        def getLinks(self, version, user_version):
            if self._x != None:
                return [self._x]
            else:
                return []

        def getRefs(self):
            if self._x != None:
                return [self._x]
            else:
                return []

    class Ptr(Ref):
        _isTemplate = True
        _hasLinks = True
        _hasRefs = False
        
        def __str__(self):
            # avoid infinite recursion
            return '%s instance at 0x%08X'%(self._x.__class__, id(self._x))

        def getRefs(self):
            return []

    class LineString(BasicBase):
        """Basic type for strings ending in a newline character (0x0a).

        >>> from tempfile import TemporaryFile
        >>> f = TemporaryFile()
        >>> l = NifFormat.LineString()
        >>> f.write('abcdefg\\x0a')
        >>> f.seek(0)
        >>> l.read(f = f)
        >>> str(l)
        'abcdefg'
        >>> f.seek(0)
        >>> l.setValue('Hi There')
        >>> l.write(f = f)
        >>> f.seek(0)
        >>> m = NifFormat.LineString()
        >>> m.read(f = f)
        >>> str(m)
        'Hi There'
        """
        def __init__(self, template = None, argument = None):
            self.setValue('')

        def getValue(self):
            return self._x

        def setValue(self, value):
            self._x = str(value).rstrip('\x0a')

        def __str__(self):
            s = BasicBase.__str__(self)
            if not s: return '<EMPTY STRING>'
            return s

        def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
            self._x = f.readline().rstrip('\x0a')

        def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
            f.write("%s\x0a"%self._x)

    class HeaderString(BasicBase):
        def __init__(self, template = None, argument = None):
            pass

        def __str__(self):
            return 'NetImmerse/Gamebryo File Format, Version x.x.x.x'

        def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
            version_string = self.versionString(version)
            s = f.read(len(version_string) + 1)
            if s != version_string + '\x0a':
                raise ValueError("invalid NIF header: expected '%s' but got '%s'"%(version_string, s[:-1]))

        def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
            f.write(self.versionString(version) + '\x0a')

        @staticmethod
        def versionString(version):
            """Transforms version number into a version string.

            >>> NifFormat.HeaderString.versionString(0x03000300)
            'NetImmerse File Format, Version 3.03'
            >>> NifFormat.HeaderString.versionString(0x03010000)
            'NetImmerse File Format, Version 3.1'
            >>> NifFormat.HeaderString.versionString(0x0A000100)
            'NetImmerse File Format, Version 10.0.1.0'
            >>> NifFormat.HeaderString.versionString(0x0A010000)
            'Gamebryo File Format, Version 10.1.0.0'
            """
            if version <= 0x0A000102:
                s = "NetImmerse"
            else:
                s = "Gamebryo"
            if version == 0x03000300:
                v = "3.03"
            elif version <= 0x03010000:
                v = "%i.%i"%((version >> 24) & 0xff, (version >> 16) & 0xff)
            else:
                v = "%i.%i.%i.%i"%((version >> 24) & 0xff, (version >> 16) & 0xff, (version >> 8) & 0xff, version & 0xff)
            return "%s File Format, Version %s"%(s, v)

    class FileVersion(BasicBase):
        def __init__(self, template = None, argument = None):
            pass

        def getValue(self):
            raise NotImplementedError

        def setValue(self, value):
            raise NotImplementedError

        def __str__(self):
            return 'x.x.x.x'

        def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
            ver, = struct.unpack('<I', f.read(4))
            if ver != version:
                raise ValueError('invalid version number: expected 0x%08X but got 0x%08X'%(version, ver))

        def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
            f.write(struct.pack('<I', version))

    class string(BasicBase):
        """Basic type for strings.

        >>> from tempfile import TemporaryFile
        >>> f = TemporaryFile()
        >>> s = NifFormat.string()
        >>> f.write('\\x07\\x00\\x00\\x00abcdefg')
        >>> f.seek(0)
        >>> s.read(f = f)
        >>> str(s)
        'abcdefg'
        >>> f.seek(0)
        >>> s.setValue('Hi There')
        >>> s.write(f = f)
        >>> f.seek(0)
        >>> m = NifFormat.string()
        >>> m.read(f = f)
        >>> str(m)
        'Hi There'
        """
        def __init__(self, template = None, argument = None):
            self.setValue('')

        def getValue(self):
            return self._x

        def setValue(self, value):
            if len(value) > 10000: raise ValueError('string too long')
            self._x = str(value)

        def __str__(self):
            s = self._x
            if not s: return '<EMPTY STRING>'
            return s

        def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
            n, = struct.unpack('<I', f.read(4))
            if n > 10000: raise ValueError('string too long (0x%08X at 0x%08X)'%(n, f.tell()))
            self._x = f.read(n)

        def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
            f.write(struct.pack('<I', len(self._x)))
            f.write(self._x)

    class ShortString(BasicBase):
        """Another type for strings."""
        def __init__(self, template = None, argument = None):
            self._x = ''

        def getValue(self):
            return self._x

        def setValue(self, value):
            if len(value) > 254: raise ValueError('string too long')
            self._x = str(value)

        def __str__(self):
            s = self._x
            if not s: return '<EMPTY STRING>'
            return s

        def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
            n, = struct.unpack('<B', f.read(1))
            self._x = f.read(n).rstrip('\x00')

        def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
            f.write(struct.pack('<B', len(self._x)+1))
            f.write(self._x + '\x00')

    # other types with internal implementation
    class FilePath(string):
        pass



    # exceptions
    class NifError(StandardError):
        pass

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        >>> hex(NifFormat.versionNumber('3.14.15.29'))
        '0x30e0f1d'
        >>> hex(NifFormat.versionNumber('1.2'))
        '0x1020000'
        >>> hex(NifFormat.versionNumber('3.03'))
        '0x3000300'
        """
        
        if version_str == '3.03': return 0x03000300 # 3.03 case is special

        try:
            ver_list = [int(x) for x in version_str.split('.')]
        except ValueError:
            return -1 # version not supported (i.e. version_str '10.0.1.3a' would trigger this)
        if len(ver_list) > 4 or len(ver_list) < 1:
            return -1 # version not supported
        for ver_digit in ver_list:
            if (ver_digit | 0xff) > 0xff:
                return -1 # version not supported
        while len(ver_list) < 4: ver_list.append(0)
        return (ver_list[0] << 24) + (ver_list[1] << 16) + (ver_list[2] << 8) + ver_list[3]

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable by python.

        >>> NifFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """
        
        parts = str(name).replace("?", "X").split() # str(name) converts name to string in case name is a unicode string
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    @classmethod
    def getVersion(cls, f):
        """Returns version and user version number, if version is supported.
        Returns -1, 0 if version is not supported.
        Returns -2, 0 if <f> is not a nif file.
        """
        pos = f.tell()
        try:
            s = f.readline(64).rstrip()
        finally:
            f.seek(pos)
        if s.startswith("NetImmerse File Format, Version " ):
            version_str = s[32:]
        elif s.startswith("Gamebryo File Format, Version "):
            version_str = s[30:]
        else:
            return -2, 0 # not a nif file
        try:
            ver = cls.versionNumber(version_str)
        except:
            return -1, 0 # version not supported
        if not ver in cls.versions.values():
            return -1, 0 # unsupported version
        # check version integer and user version
        userver = 0
        if ver >= 0x0303000D:
            ver_int = None
            try:
                f.readline(64)
                ver_int, = struct.unpack('<I', f.read(4))
                if ver_int != ver:
                    return -2, 0 # not a nif file
                if ver >= 0x14000004: f.read(1)
                if ver >= 0x0A010000: userver, = struct.unpack('<I', f.read(4))
            finally:
                f.seek(pos)
        return ver, userver

    @classmethod
    def read(cls, version, user_version, f, verbose = 0):
        # read header
        if verbose >= 1:
            print "reading block at 0x%08X..."%f.tell()
        hdr = cls.Header()
        link_stack = [] # list of indices, as they are added to the stack
        hdr.read(version, user_version, f, link_stack, None)
        assert(link_stack == []) # there should not be any links in the header
        if verbose >= 2:
            print hdr

        # read the blocks
        block_dct = {} # maps block index to actual block
        block_list = [] # records all blocks as read from the nif file in the proper order
        block_num = 0 # the current block numner

        if version < 0x0303000D:
            # skip 'Top Level Object' block type
            top_level_str = cls.string()
            top_level_str.read(version, user_version, f, link_stack, None)
            top_level_str = str(top_level_str)
            if not top_level_str == "Top Level Object":
                raise cls.NifError("expected 'Top Level Object' but got '%s' instead"%top_level_str)

        while True:
            # get block name
            if version >= 0x05000001:
                if version <= 0x0A01006A:
                    dummy, = struct.unpack('<I', f.read(4))
                    if dummy != 0:
                        raise cls.NifError('non-zero block tag 0x%08X at 0x%08X)'%(dummy, f.tell()))
                block_type = hdr.blockTypes[hdr.blockTypeIndex[block_num]]
            else:
                block_type = cls.string()
                block_type.read(version, user_version, f, link_stack, None)
                block_type = str(block_type)
            # get the block index
            if version >= 0x0303000D:
                # for these versions the block index is simply the block number
                block_index = block_num
            else:
                # earlier versions
                # the number of blocks is not in the header
                # and a special block type string marks the end of the file
                if block_type == "End Of File": break
                # read the block index, which is probably the memory
                # location of the object when it was written to
                # memory
                else:
                    block_index, = struct.unpack('<I', f.read(4))
                    if block_dct.has_key(block_index):
                        raise cls.NifError('duplicate block index (0x%08X at 0x%08X)'%(block_index, f.tell()))
            # create and read block
            try:
                block = getattr(cls, block_type)()
            except AttributeError:
                raise cls.NifError("unknown block type '" + block_type + "'")
            if verbose >= 1:
                print "reading block at 0x%08X..."%f.tell()
            try:
                block.read(version, user_version, f, link_stack, None)
            except:
                if verbose >= 1:
                    print "reading failed"
                if verbose >= 2:
                    print "link stack ", link_stack
                    print "block that failed:"
                    print block
                elif verbose >= 1:
                    print block.__class__
                raise
            block_dct[block_index] = block
            block_list.append(block)
            if verbose >= 2:
                print block
            elif verbose >= 1:
                print block.__class__
            # check if we are done
            block_num += 1
            if version >= 0x0303000D:
                if block_num >= hdr.numBlocks: break

        # read footer
        ftr = cls.Footer()
        ftr.read(version, user_version, f, link_stack, None)

        # check if we are at the end of the file
        if f.read(1) != '':
            raise cls.NifError('end of file not reached: corrupt nif file?')

        # fix links
        for block in block_list:
            block.fixLinks(version, user_version, block_dct, link_stack)
        ftr.fixLinks(version, user_version, block_dct, link_stack)
        if link_stack != []:
            raise cls.NifError('not all links have been popped from the stack (bug?)')
        # return root objects
        roots = []
        if version >= 0x0303000D:
            for root in ftr.roots:
                roots.append(root)
        else:
            if block_num > 0:
                roots.append(block_list[0])
        return roots

    @classmethod
    def write(cls, version, user_version, f, roots, verbose = 0):
        # set up index and type dictionary
        block_list = [] # list of all blocks to be written
        block_index_dct = {} # maps block to block index
        block_type_list = [] # list of all block type strings
        block_type_dct = {} # maps block to block type string index
        for root in roots:
            cls._makeBlockList(version, user_version, root, block_list, block_index_dct, block_type_list, block_type_dct)

        # set up header
        hdr = cls.Header()
        hdr.userVersion = user_version # TODO dedicated type for userVersion similar to FileVersion
        hdr.userVersion2 = 11 # for oblivion CS; apparently this is the version of the bhk blocks
        hdr.numBlocks = len(block_list)
        hdr.numBlockTypes = len(block_type_list)
        hdr.blockTypes.updateSize()
        for i, block_type in enumerate(block_type_list):
            hdr.blockTypes[i] = block_type
        hdr.blockTypeIndex.updateSize()
        for i, block in enumerate(block_list):
            hdr.blockTypeIndex[i] = block_type_dct[block]
        if verbose >= 2:
            print hdr

        # set up footer
        ftr = cls.Footer()
        ftr.numRoots = len(roots)
        ftr.roots.updateSize()
        for i, root in enumerate(roots):
            ftr.roots[i] = root

        # write the file
        hdr.write(version, user_version, f, block_index_dct, None)
        if version < 0x0303000D:
            s = cls.string()
            s.setValue("Top Level Object")
            s.write(version, user_version, f, block_index_dct, None)
        for block in block_list:
            if version >= 0x05000001:
                if version <= 0x0A01006A:
                    f.write('\x00\x00\x00\x00') # write zero dummy separator
            else:
                # write block type string
                s = cls.string()
                assert(block_type_list[block_type_dct[block]] == block.__class__.__name__) # debug
                s.setValue(block.__class__.__name__)
                s.write(version, user_version, f, block_index_dct, None)
            # write block index
            if verbose >= 1:
                print "writing block %i..."%block_index_dct[block]
            if version < 0x0303000D:
                f.write(struct.pack('<i', block_index_dct[block])[0])
            # write block
            block.write(version, user_version, f, block_index_dct, None)
        if version < 0x0303000D:
            s = cls.string()
            s.setValue("End Of File")
            s.write(version, user_version, f, block_index_dct, None)
        ftr.write(version, user_version, f, block_index_dct, None)

    @classmethod
    def _makeBlockList(cls, version, user_version, root, block_list, block_index_dct, block_type_list, block_type_dct, reverse = False):
        """This is a helper function for write to set up the list of all blocks,
        the block index map, and the block type map."""
        # block already listed? if so, return
        if root in block_list: return
        # add block type to block type dictionary
        block_type = root.__class__.__name__
        try:
            block_type_dct[root] = block_type_list.index(block_type)
        except ValueError:
            block_type_dct[root] = len(block_type_list)
            block_type_list.append(block_type)
        # check if we need to add children first (required for oblivion)
        if isinstance(root, cls.bhkRigidBody) or isinstance(root, cls.bhkCollisionObject):
            reverse = True
        # add block if not reverse
        if not reverse:
            if version >= 0x0303000D:
                block_index_dct[root] = len(block_list)
            else:
                block_index_dct[root] = id(root)
            block_list.append(root)
        # add children
        for child in root.getLinks(version, user_version):
            cls._makeBlockList(version, user_version, child, block_list, block_index_dct, block_type_list, block_type_dct, reverse)
        # add block if reverse
        if reverse:
            block_index_dct[root] = len(block_list)
            block_list.append(root)

    @classmethod
    def walk(cls, top, topdown = True, onerror = None, verbose = 0):
        """A generator which yields the roots of all files in directory top
        whose filename matches the regular expression re_filename. The argument
        top can also be a file instead of a directory. The argument onerror,
        if set, will be called if cls.read raises an exception (errors coming
        from os.walk will be ignored)."""
        for version, user_version, f, roots in walkFile(cls, top, topdown, onerror, verbose):
            yield roots

    @classmethod
    def walkFile(cls, top, topdown = True, onerror = None, verbose = 0, mode = 'rb'):
        """Like walk, but returns more information:
        version, user_version, f, and roots.

        Note that the caller is not responsible for closing f.

        walkFile is for instance used by runtest.py to implement the
        testFile-style tests which must access f after the file has been read."""
        # filter for recognizing nif files by extension
        # .kf are nif files containing keyframes
        # .kfa are nif files containing keyframes in DAoC style
        # .nifcache are Empire Earth II nif files
        re_nif = re.compile(r'^.*\.(nif|kf|kfa|nifcache)$', re.IGNORECASE)
        # now walk over all these files in directory top
        for filename in Utils.walk(top, topdown, onerror = None, re_filename = re_nif):
            if verbose >= 1: print "reading %s"%filename
            f = open(filename, mode)
            try:
                # get the version
                version, user_version = cls.getVersion(f)
                if version >= 0:
                    # we got it, so now read the nif file
                    if verbose >= 2: print "version 0x%08X"%version
                    try:
                        # return (version, user_version, f, roots)
                        yield version, user_version, f, cls.read(version, user_version, f)
                    except StandardError, e:
                        # an error occurred during reading
                        # this should not happen: means that the file is
                        # corrupt, or that the xml is corrupt
                        # so we call onerror
                        if verbose >= 1:
                            print 'Warning: read failed due to either a corrupt nif file, a corrupt nif.xml,'
                            print 'or a bug in NifFormat library.'
                        if verbose >= 2:
                            Utils.hexDump(f)
                        if onerror == None:
                            pass # ignore the error
                        else:
                            onerror(e)
                # getting version failed, do not raise an exception
                # but tell user what happened
                elif version == -1:
                    if verbose >= 1: print 'version not supported'
                else:
                    if verbose >= 1: print 'not a nif file'
            finally:
                f.close()
