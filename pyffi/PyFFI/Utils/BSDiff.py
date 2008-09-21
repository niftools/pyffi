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

class ByteArray:
    """A byte array which behaves like a C pointer."""
    def __init__(self, data):
        self._data = array("c", data)
        self._pos = 0

    def __getitem__(self, index):
        return self._data[self._pos + index]

    def __setitem__(self, index, value):
        self._data[self._pos + index] = value

    def __add__(self, index):
        self._pos += index

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
                elif V[I[k + i] + h] == x:
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
        elif V[I[i] + h] == x:
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
##    off_t scan,pos,length;
##    off_t lastscan,lastpos,lastoffset;
##    off_t oldscore,scsc;
##    off_t s,Sf,lengthf,Sb,lengthb;
##    off_t overlap,Ss,lengths;
##    off_t i;
##    off_t dblength,eblength;
##    u_char *db,*eb;
##    u_char buf[8];
##    u_char header[32];
##    FILE * pf;
##    BZFILE * pfbz2;
##    int bz2err;

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
    db = array("c", ("\x00" for i in xrange(newsize + 1)))
    eb = array("c", ("\x00" for i in xrange(newsize + 1)))
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
    pf.write(struct.pack("Q", 0))
    pf.write(struct.pack("Q", 0))
    pf.write(struct.pack("Q", newsize))

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

            if(lastscan+lengthf>scan-lengthb) {
                overlap=(lastscan+lengthf)-(scan-lengthb);
                s=0;Ss=0;lengths=0;
                for(i=0;i<overlap;i += 1) {
                    if(new[lastscan+lengthf-overlap+i]==
                       old[lastpos+lengthf-overlap+i]) s += 1;
                    if(new[scan-lengthb+i]==
                       old[pos-lengthb+i]) s--;
                    if(s>Ss) { Ss=s; lengths=i+1; };
                };

                lengthf+=lengths-overlap;
                lengthb-=lengths;
            };

            for(i=0;i<lengthf;i += 1)
                db[dblength+i]=new[lastscan+i]-old[lastpos+i];
            for(i=0;i<(scan-lengthb)-(lastscan+lengthf);i += 1)
                eb[eblength+i]=new[lastscan+lengthf+i];

            dblength+=lengthf;
            eblength+=(scan-lengthb)-(lastscan+lengthf);

            offtout(lengthf,buf);
            BZ2_bzWrite(&bz2err, pfbz2, buf, 8);
            if (bz2err != BZ_OK)
                errx(1, "BZ2_bzWrite, bz2err = %d", bz2err);

            offtout((scan-lengthb)-(lastscan+lengthf),buf);
            BZ2_bzWrite(&bz2err, pfbz2, buf, 8);
            if (bz2err != BZ_OK)
                errx(1, "BZ2_bzWrite, bz2err = %d", bz2err);

            offtout((pos-lengthb)-(lastpos+lengthf),buf);
            BZ2_bzWrite(&bz2err, pfbz2, buf, 8);
            if (bz2err != BZ_OK)
                errx(1, "BZ2_bzWrite, bz2err = %d", bz2err);

            lastscan=scan-lengthb;
            lastpos=pos-lengthb;
            lastoffset=pos-scan;
        };
    };
    BZ2_bzWriteClose(&bz2err, pfbz2, 0, NULL, NULL);
    if (bz2err != BZ_OK)
        errx(1, "BZ2_bzWriteClose, bz2err = %d", bz2err);

    /* Compute size of compressed ctrl data */
    if ((length = ftello(pf)) == -1)
        err(1, "ftello");
    offtout(length-32, header + 8);

    /* Write compressed diff data */
    if ((pfbz2 = BZ2_bzWriteOpen(&bz2err, pf, 9, 0, 0)) == NULL)
        errx(1, "BZ2_bzWriteOpen, bz2err = %d", bz2err);
    BZ2_bzWrite(&bz2err, pfbz2, db, dblength);
    if (bz2err != BZ_OK)
        errx(1, "BZ2_bzWrite, bz2err = %d", bz2err);
    BZ2_bzWriteClose(&bz2err, pfbz2, 0, NULL, NULL);
    if (bz2err != BZ_OK)
        errx(1, "BZ2_bzWriteClose, bz2err = %d", bz2err);

    /* Compute size of compressed diff data */
    if ((newsize = ftello(pf)) == -1)
        err(1, "ftello");
    offtout(newsize - length, header + 16);

    /* Write compressed extra data */
    if ((pfbz2 = BZ2_bzWriteOpen(&bz2err, pf, 9, 0, 0)) == NULL)
        errx(1, "BZ2_bzWriteOpen, bz2err = %d", bz2err);
    BZ2_bzWrite(&bz2err, pfbz2, eb, eblength);
    if (bz2err != BZ_OK)
        errx(1, "BZ2_bzWrite, bz2err = %d", bz2err);
    BZ2_bzWriteClose(&bz2err, pfbz2, 0, NULL, NULL);
    if (bz2err != BZ_OK)
        errx(1, "BZ2_bzWriteClose, bz2err = %d", bz2err);

    /* Seek to the beginning, write the header, and close the file */
    if (fseeko(pf, 0, SEEK_SET))
        err(1, "fseeko");
    if (fwrite(header, 32, 1, pf) != 1)
        err(1, "fwrite(%s)", argv[3]);
    if (fclose(pf))
        err(1, "fclose");

    /* Free the memory we used */
    free(db);
    free(eb);
    free(I);
    free(old);
    free(new);

    return 0;
