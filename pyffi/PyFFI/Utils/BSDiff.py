"""A port of the bsdiff algorithm to Python
(see http://www.daemonology.net/bsdiff/).

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

#
# This file is based on bsdiff.c and bspatch.c which are
# Copyright 2003-2005 Colin Percival
# See http://www.daemonology.net/bsdiff/
#

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

from array import array
import bz2
from cStringIO import StringIO
import struct
import os

class ByteArray:
    """A byte array which behaves somewhat like a C pointer."""
    def __init__(self, data = None):
        if data is None:
            self._data = array("B")
        else:
            self._data = array("B", data)
        self._pos = 0

    def __getitem__(self, index):
        return self._data[self._pos + index]

    def __setitem__(self, index, value):
        self._data[self._pos + index] = value

    def __add__(self, index):
        result = ByteArray()
        result._data = self._data
        result._pos = self._pos + index
        return result

def split(I, V, start, length, h):
    if length < 16:
        k = start
        while k < start + length:
            j = 1
            x = V[I[k] + h]
            i = 1
            while k + i < start + length:
                if V[I[k + i] + h] < x:
                    x = V[I[k + i] + h]
                    j = 0
                if V[I[k + i] + h] == x:
                    tmp = I[k + j]
                    I[k + j] = I[k + i]
                    I[k + i] = tmp
                    j += 1
                i += 1
            for i in xrange(j):
                V[I[k + i]] = k + j - 1
            if j == 1:
                I[k] = -1
            k += j
        return

    x = V[I[(start + length) // 2] + h]
    jj=0
    kk=0
    for i in xrange(start, start + length):
        if V[I[i] + h] < x:
            jj += 1
        if V[I[i] + h] == x:
            kk += 1
    jj += start
    kk += jj

    i = start
    j=0
    k=0
    while i < jj:
        if V[I[i] + h] < x:
            i += 1
        elif V[I[i] + h] == x:
            tmp = I[i]
            I[i] = I[jj + j]
            I[jj + j] = tmp
            j += 1
        else:
            tmp = I[i]
            I[i] = I[kk + k]
            I[kk + k] = tmp
            k += 1

    while jj + j < kk:
        if V[I[jj + j] + h] == x:
            j += 1
        else:
            tmp = I[jj + j]
            I[jj + j] = I[kk + k]
            I[kk + k] = tmp
            k += 1

    if jj > start:
        split(I, V, start, jj - start, h)

    for i in xrange(kk-jj):
        V[I[jj + i]] = kk - 1
    if jj == kk - 1:
        I[jj] = -1

    if start + length > kk:
        split(I, V, kk, start + length - kk, h)

def qsufsort(I, V, old, oldsize):
    buckets = [0 for i in xrange(256)]
    for i in xrange(oldsize):
        buckets[old[i]] += 1
    for i in xrange(1, 256):
        buckets[i] += buckets[i - 1]
    for i in xrange(255, 0, -1):
        buckets[i] = buckets[i - 1]
    buckets[0] = 0

    for i in xrange(oldsize):
        buckets[old[i]] += 1
        I[buckets[old[i]]] = i
    I[0] = oldsize
    for i in xrange(oldsize):
        V[i] = buckets[old[i]]
    V[oldsize] = 0
    for i in xrange(1, 256):
        if buckets[i] == buckets[i - 1] + 1:
            I[buckets[i]] = -1
    I[0] = -1

    h = 1
    while I[0] != -(oldsize + 1):
        length = 0
        i = 0
        while i < oldsize + 1:
            if I[i] < 0:
                length -= I[i]
                i -= I[i]
            else:
                if length:
                    I[i - length] = -length
                length = V[I[i]] + 1 - i
                split(I, V, i, length, h)
                i += length
                length = 0
        if length:
            I[i - length] = -length;
        h += h

    for i in xrange(oldsize+1):
        I[V[i]] = i

def matchlength(old, oldsize, new, newsize):
    for i in xrange(min(oldsize, newsize)):
        if old[i] != new[i]:
            return i
    return min(oldsize, newsize) + 1

# wrapper
def memcmp(buf1, buf2, size):
    for i in xrange(size):
        result = cmp(buf1[i], buf2[i])
        if result:
            return result
    # equal
    return 0

# note: returns offset and pos (C function returned pos via pointer argument)
def search(I, old, oldsize, new, newsize, st, en):
    if en-st < 2:
        x = matchlength(old+I[st],oldsize-I[st],new,newsize)
        y = matchlength(old+I[en],oldsize-I[en],new,newsize)
        if x > y:
            return I[st], x
        else:
            return I[en], y

    x = st + (en - st) // 2
    if(memcmp(old+I[x],new,min(oldsize-I[x],newsize))<0):
        return search(I,old,oldsize,new,newsize,x,en)
    else:
        return search(I,old,oldsize,new,newsize,st,x)

def diff(oldfile, newfile, patchfile):
    # argv[1] in C function is oldfile
    olddata = oldfile.read()
    oldsize = len(olddata)
    old = ByteArray(olddata)
    del olddata

    I = [0 for i in xrange(oldsize + 1)]
    V = [0 for i in xrange(oldsize + 1)]

    qsufsort(I, V, old, oldsize)

    del V

    # argv[2] in C function is newfile
    newdata = newfile.read()
    newsize = len(newdata)
    new = ByteArray(newdata)
    del newdata

    # no need to use db and eb as pointers, so array will do instead of
    # ByteArray
    db = array("B", (0 for i in xrange(newsize + 1)))
    eb = array("B", (0 for i in xrange(newsize + 1)))
    dblength=0
    eblength=0

    # pf is patchfile in C function
    pf = patchfile 

    # Header is
    #    0   8    "BSDIFF40"
    #    8   8   length of bzip2ed ctrl block
    #    16  8   length of bzip2ed diff block
    #    24  8   length of new file
    # File is
    #    0   32  Header
    #    32  ??  Bzip2ed ctrl block
    #    ??  ??  Bzip2ed diff block
    #    ??  ??  Bzip2ed extra block

    pf.write("BSDIFF40")
    pf.write(struct.pack("<q", 0))
    pf.write(struct.pack("<q", 0))
    pf.write(struct.pack("<q", newsize))

    # Compute the differences, writing ctrl as we go
    pfbz2 = bz2.BZ2Compressor()
    scan = 0
    length = 0
    lastscan = 0
    lastpos = 0
    lastoffset = 0
    while scan < newsize:
        oldscore = 0
        # original was scsc=scan+=length
        # C processes assignments from right to left
        scan += length
        scsc = scan
        while scan < newsize:
            # search returns pos and length (unlike C function)
            pos, length = search(I,old,oldsize,new+scan,newsize-scan,
                                 0,oldsize)

            while scsc < scan + length:
                if((scsc+lastoffset<oldsize) and
                    (old[scsc+lastoffset] == new[scsc])):
                    oldscore += 1
                scsc += 1

            if (((length==oldscore) and (length!=0)) or
                (length>oldscore+8)):
                break

            if ((scan+lastoffset<oldsize) and
                (old[scan+lastoffset] == new[scan])):
                oldscore -= 1
            scan += 1

        if((length!=oldscore) or (scan==newsize)):
            s = 0
            Sf = 0
            lengthf = 0
            i = 0
            while (lastscan+i<scan)and(lastpos+i<oldsize):
                if (old[lastpos+i]==new[lastscan+i]):
                    s += 1
                i += 1
                if(s*2-i>Sf*2-lengthf):
                    Sf = s
                    lengthf = i

            lengthb=0
            if(scan<newsize):
                s = 0
                Sb = 0
                i = 1
                while (scan>=lastscan+i)and(pos>=i):
                    if(old[pos-i]==new[scan-i]):
                        s += 1;
                    if(s*2-i>Sb*2-lengthb):
                        Sb = s
                        lengthb = i
                    i += 1

            if(lastscan+lengthf>scan-lengthb):
                overlap=(lastscan+lengthf)-(scan-lengthb)
                s=0
                Ss=0
                lengths=0
                for i in xrange(overlap):
                    if(new[lastscan+lengthf-overlap+i]==
                       old[lastpos+lengthf-overlap+i]):
                        s += 1
                    if(new[scan-lengthb+i]==
                       old[pos-lengthb+i]):
                        s -= 1
                    if(s>Ss):
                        Ss=s
                        lengths=i+1

                lengthf += lengths-overlap
                lengthb -= lengths

            for i in xrange(lengthf):
                db[dblength+i]=new[lastscan+i]-old[lastpos+i]
            for i in xrange((scan-lengthb)-(lastscan+lengthf)):
                eb[eblength+i]=new[lastscan+lengthf+i]

            dblength+=lengthf
            eblength+=(scan-lengthb)-(lastscan+lengthf)

            pf.write(pfbz2.compress(
                struct.pack("<q", length)))
            pf.write(pfbz2.compress(
                struct.pack("<q", (scan-lengthb)-(lastscan+lengthf))))
            pf.write(pfbz2.compress(
                struct.pack("<q", (pos-lengthb)-(lastpos+lengthf))))

            # DEBUG
            print "ctrl", (length,
                           (scan-lengthb)-(lastscan+lengthf),
                           (pos-lengthb)-(lastpos+lengthf))

            lastscan=scan-lengthb
            lastpos=pos-lengthb
            lastoffset=pos-scan

    pf.write(pfbz2.flush())

    # Compute size of compressed ctrl data
    ctrl_endpos = pf.tell()

    # Write compressed diff data
    pf.write(bz2.compress(db[:dblength].tostring()))

    # Compute size of compressed diff data
    diff_endpos = pf.tell()

    # Write compressed extra data
    pf.write(bz2.compress(eb[:eblength].tostring()))

    # seek to the beginning and write the header
    pf.seek(8)
    pf.write(struct.pack("<q", ctrl_endpos - 32))
    pf.write(struct.pack("<q", diff_endpos - ctrl_endpos))
    pf.seek(0, os.SEEK_END)

def patch(oldfile, newfile, patchfile):
    # f is patchfile in C function
    f = patchfile

    
    # File format:
    #    0   8   "BSDIFF40"
    #    8   8   X
    #    16  8   Y
    #    24  8   sizeof(newfile)
    #    32  X   bzip2(control block)
    #    32+X    Y   bzip2(diff block)
    #    32+X+Y  ??? bzip2(extra block)
    # with control block a set of triples (x,y,z) meaning "add x bytes
    # from oldfile to x bytes from the diff block; copy y bytes from the
    # extra block; seek forwards in oldfile by z bytes".

    # Read header
    if f.read(8) != "BSDIFF40":
        raise ValueError("corrupt patch")

    # Read lengths from header
    bzctrllen, bzdatalen, newsize = struct.unpack("<qqq", f.read(24))
    if((bzctrllen<0) or (bzdatalen<0) or (newsize<0)):
        raise ValueError("corrupt patch")

    # C function opens compressed streams with libbzip2 at the right places
    # and sequentially decompresses the data
    # this implementation decompresses everything in one shot
    # and uses a memory stream to each part
    cpf = StringIO(bz2.decompress(f.read(bzctrllen)))
    dpf = StringIO(bz2.decompress(f.read(bzdatalen)))
    epf = StringIO(bz2.decompress(f.read()))

    # read old file
    olddata = oldfile.read()
    oldsize = len(olddata)
    old = ByteArray(olddata)
    del olddata

    # allocate new data
    new = array("B")

    # DEBUG
    print "old size", oldsize
    print "new size", newsize

    oldpos=0
    newpos=0
    while(newpos<newsize):
        # Read control data
        ctrl = struct.unpack("<qqq", cpf.read(24))

        # DEBUG
        print "ctrl", ctrl

        # Sanity-check
        if(newpos+ctrl[0]>newsize):
            raise ValueError("corrupt patch")

        # Read diff string
        new.fromstring(dpf.read(ctrl[0]))

        # Add old data to diff string
        for i in xrange(ctrl[0]):
            # TODO optimize this range check by putting it in the xrange
            if((oldpos+i>=0) and (oldpos+i<oldsize)):
                new[newpos+i]+=old[oldpos+i]

        # Adjust pointers
        newpos+=ctrl[0]
        oldpos+=ctrl[0]

        # Sanity-check
        if(newpos+ctrl[1]>newsize):
            raise ValueError("corrupt patch %s")

        # Read extra string
        new.fromstring(epf.read(ctrl[1]))

        # Adjust pointers
        newpos += ctrl[1]
        oldpos += ctrl[2]

    # Write the new file
    new.tofile(newfile)

if __name__ == "__main__":
#    import doctest
#    doctest.testmod()
    from cStringIO import StringIO
    a = StringIO("qabxcdafhjaksdhuaeuhuhasf")
    b = StringIO("abycdfafhjajsadjkahgeruiofssq")
    p = StringIO()
    diff(a, b, p)
    c = StringIO()
    a.seek(0)
    p.seek(0)
    patch(a, c, p)
