"""A wrapper around difflib.SequenceMatcher to create and apply binary
patches.

>>> from cStringIO import StringIO
>>> a = StringIO("qabxcdafhjaksdhuaeuhuhasf")
>>> b = StringIO("abycdfafhjajsadjkahgeruiofssq")
>>> p = StringIO()
>>> diff(a, b, p)
>>> c = StringIO()
>>> p.seek(0)
>>> patch(a, c, p)
>>> b.getvalue() == c.getvalue()
True
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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

from difflib import SequenceMatcher
import os
import struct
import zlib

OPCODES = ["replace", "delete", "insert", "equal"]
MAGIC = "\x0d\x01\x0f\x00"  # 'DIF0', header of patch files

def diff(oldfile, newfile, patchfile):
    """Writes binary date to patchfile which describes how to turn oldfile
    into newfile. Note that the caller must close patchfile."""

    # reset streams
    oldfile.seek(0)
    newfile.seek(0)

    # read data
    olddata = oldfile.read()
    newdata = newfile.read()

    # diff version string
    patchfile.write(MAGIC)

    # write hashes for data integrity
    patchfile.write(struct.pack("<i", zlib.crc32(olddata)))
    patchfile.write(struct.pack("<i", zlib.crc32(newdata)))
    
    seqmatch = SequenceMatcher(None, olddata, newdata)
    newfile.seek(0)
    for tag, i1, i2, j1, j2 in seqmatch.get_opcodes():
        patchfile.write(struct.pack("<B", OPCODES.index(tag) + 0xf0))
        if tag == "replace":
            patchfile.write(struct.pack("<II", i2 - i1, j2 - j1))
            patchfile.write(newfile.read(j2 - j1))
        elif tag == "delete":
            patchfile.write(struct.pack("<I", i2 - i1))
        elif tag == "insert":
            patchfile.write(struct.pack("<I", j2 - j1))
            patchfile.write(newfile.read(j2 - j1))
        elif tag == "equal":
            patchfile.write(struct.pack("<I", i2 - i1))
            newfile.seek(i2 - i1, os.SEEK_CUR)
    patchfile.write(struct.pack("<B", 255))
    oldfile.seek(0)
    newfile.seek(0)

def patch(oldfile, newfile, patchfile):
    """Writes newfile based on oldfile and patchfile generated previously with
    L{diff}."""
    # reset streams
    oldfile.seek(0)
    newfile.seek(0)

    # check header
    if patchfile.read(4) != MAGIC:
        raise ValueError("patch file corrupted (invalid header)")

    # read checksums
    oldcrc32, = struct.unpack("<i", patchfile.read(4))
    newcrc32, = struct.unpack("<i", patchfile.read(4))

    # read data and check checksum
    if oldcrc32 != zlib.crc32(oldfile.read()):
        raise ValueError("patch does not match source file (invalid checksum)")
    oldfile.seek(0)

    while True:
        tagbyte, = struct.unpack("<B", patchfile.read(1))
        if tagbyte == 255:
            # done!
            break
        tag = OPCODES[tagbyte - 0xf0]
        if tag == "replace":
            i12, j12 = struct.unpack("<II", patchfile.read(8))
            oldfile.seek(i12, os.SEEK_CUR)
            newfile.write(patchfile.read(j12))
        elif tag == "delete":
            i12, = struct.unpack("<I", patchfile.read(4))
            oldfile.seek(i12, os.SEEK_CUR)
        elif tag == "insert":
            j12, = struct.unpack("<I", patchfile.read(4))
            newfile.write(patchfile.read(j12))
        elif tag == "equal":
            i12, = struct.unpack("<I", patchfile.read(4))
            newfile.write(oldfile.read(i12))
        else:
            raise RuntimeError("patch corrupted (unexpected opcode %i)"
                               % tagbyte)

    # check checksum of written data
    newfile.seek(0)
    if newcrc32 != zlib.crc32(newfile.read()):
        raise RuntimeError("patch applied but crc32 does not match")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
