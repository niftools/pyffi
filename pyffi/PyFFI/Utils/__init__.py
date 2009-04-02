"""This module bundles various general purpose utilities:
- hexdumping
- parsing all files in a directory tree
- 3D related tasks (see TriStrip.py, MathUtils.py, QuickHull.py, and Inertia.py)
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

import os

def walk(top, topdown=True, onerror=None, re_filename=None):
    """A variant of os.walk() which also works if top is a file instead of a
    directory, filters files by name, and returns full path. File names are
    returned in alphabetical order.

    @param top: The top directory or file.
    @type top: str
    @param topdown: Whether to list directories first or not.
    @type topdown: bool
    @param onerror: Which function to call when an error occurs.
    @type onerror: function
    @param re_filename: Regular expression to match file names.
    @type re_filename: compiled regular expression (see re module)
    """
    if os.path.isfile(top):
        dirpath, filename = os.path.split(top)
        if re_filename != None:
            if re_filename.match(filename):
                yield top
        else:
            yield top
    else:
        for dirpath, dirnames, filenames in os.walk(top):
            filenames = sorted(filenames)
            for filename in filenames:
                if re_filename != None:
                    if re_filename.match(filename):
                        yield os.path.join(dirpath, filename)
                else:
                    yield os.path.join(dirpath, filename)

#table = "."*32
#for c in [chr(i) for i in xrange(32,128)]:
#    table += c
#table += "."*128
chartable = '................................ !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~.................................................................................................................................'

def hexDump(f, numLines = 8):
    """A function for hexdumping.

    >>> from tempfile import TemporaryFile
    >>> f = TemporaryFile()
    >>> f.write('abcdefg\\x0a')
    >>> f.seek(2)
    >>> hexDump(f, 2)
                00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 
    -----------------------------------------------------------
    0x00000000  61 62>63 64 65 66 67 0A                         |abcdefg.        |
    0x00000010                                                  |                |
    <BLANKLINE>
    """

    dumpstr = ""

    pos = f.tell()
    if pos > numLines*8:
        f.seek((pos-numLines*8) & 0xfffffff0)
    else:
        f.seek(0)
    dumppos = f.tell()
    dumpstr += "            "
    for ofs in xrange(16):
        dumpstr += "%02X " % ofs
    dumpstr += "\n-----------------------------------------------------------\n"
    for i in xrange(numLines):
        dumpstr += "0x%08X " % dumppos
        data = f.read(16)
        for j, c in enumerate(data):
            if dumppos + j != pos:
                dumpstr += " %02X" % ord(c)
            else:
                dumpstr += ">%02X" % ord(c)
        for j in xrange(len(data), 16):
            dumpstr += "   "
            data += " "
        dumpstr += " |" + data.translate(chartable) + "|\n"
        dumppos += 16
    print(dumpstr)

