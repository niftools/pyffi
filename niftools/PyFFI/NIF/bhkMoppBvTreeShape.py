# --------------------------------------------------------------------------
# NifFormat.bhkMoppBvTreeShape
# Custom functions for bhkMoppBvTreeShape.
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

import math # math.ceil

def updateOriginScale(self):
    """Update scale and origin."""
    minx = min([v.x for v in self.shape.data.vertices])
    miny = min([v.y for v in self.shape.data.vertices])
    minz = min([v.z for v in self.shape.data.vertices])
    maxx = max([v.x for v in self.shape.data.vertices])
    maxy = max([v.y for v in self.shape.data.vertices])
    maxz = max([v.z for v in self.shape.data.vertices])
    self.origin.x = minx - 0.1
    self.origin.y = miny - 0.1
    self.origin.z = minz - 0.1
    self.scale = (256*256*254) / (0.2+max([maxx-minx,maxy-miny,maxz-minz]))

def updateTree(self):
    """Update the MOPP tree."""
    
    mopp = [] # the mopp 'assembly' script
    q = 256*256 / self.scale # quantization factor

    # opcodes
    BOUNDX = 0x26    
    BOUNDY = 0x27    
    BOUNDZ = 0x28    
    TESTX = 0x10
    TESTY = 0x11
    TESTZ = 0x12

    # add first crude bounding box checks
    maxx = math.ceil((max([v.x for v in self.shape.data.vertices]) + 0.1 - self.origin.x) / q)
    maxy = math.ceil((max([v.y for v in self.shape.data.vertices]) + 0.1 - self.origin.y) / q)
    maxz = math.ceil((max([v.z for v in self.shape.data.vertices]) + 0.1 - self.origin.z) / q)
    if maxx < 0 or maxy < 0 or maxz < 0: raise ValueError("cannot update mopp tree with invalid origin")
    if maxx > 255 or maxy > 255 or maxz > 255: raise ValueError("cannot update mopp tree with invalid scale")
    mopp.extend([BOUNDZ, 0, maxz])
    mopp.extend([BOUNDY, 0, maxy])
    mopp.extend([BOUNDX, 0, maxx])

    # add a trivial tree
    numtriangles = len(self.shape.data.triangles)
    if numtriangles > 128: raise ValueError("cannot update mopp: too many triangles") # todo: figure out how to add more
    for t in xrange(numtriangles-1):
         mopp.extend([TESTZ, maxz, 0, 1, 0x30 + t])
    mopp.extend([0x30+numtriangles-1])

    # delete mopp and replace with new data
    self.moppDataSize = len(mopp)
    self.moppData.updateSize()
    for i, b in enumerate(mopp):
        self.moppData[i] = b

# ported from NifVis/bhkMoppBvTreeShape.py
def parseTree(self, start = 0, depth = 0, toffset = 0, verbose = False):
    """If verbose is True then the mopp subtree is printed while parsed. Returns number of bytes processed and a list of triangle indices encountered."""
    mopp = self.moppData # shortcut notation
    n = 0 # number of bytes processed
    tris = [] # triangle indices
    i = start # current index
    ret = False # set to True if an opcode signals a triangle index
    while i < self.moppDataSize and not ret:
        # get opcode and print it
        code = mopp[i]
        print "  "*depth + '0x%02X'%code,

        if code == 0x09:
            # set the triangle offset for next command
            print mopp[i+1], '[ triangle offset = %i ]'%mopp[i+1]
            toffset = mopp[i+1]
            i += 2
            n += 2
            # get next command
            code = mopp[i]
            print "  "*depth + '0x%02X'%code,

        if code in xrange(0x30,0x50):
            # triangle with offset
            print '[ triangle %i ]'%(code-0x30+toffset)
            i += 1
            n += 1
            tris.append(code-0x30+toffset)
            ret = True
        elif code == 0x50:
            # triangle without offset
            print mopp[i+1], '[ triangle %i ]'%mopp[i+1]
            tris.append(mopp[i+1])
            i += 2
            n += 2
            ret = True

        elif code in [ 0x06 ]: # unsure
            print
            i += 1
            n += 1

        elif code in [ 0x05 ]: # unsure
            print mopp[i+1]
            i += 2
            n += 2

        elif code in [0x10,0x11,0x12, 0x13,0x14,0x15, 0x16,0x17,0x18, 0x19, 0x1A, 0x1C]:
            # compact if-then-else
            print mopp[i+1], mopp[i+2],
            if code == 0x10:
                print '[ branch X ]'
            elif code == 0x11:
                print '[ branch Y ]'
            elif code == 0x12:
                print '[ branch Z ]'
            else:
                print
            print "  "*depth + 'if:'
            nsub1, trissub1 = self.parseTree(start = i+4, depth = depth+1, toffset = toffset, verbose = verbose)
            print "  "*depth + 'else:'
            nsub2, trissub2 = self.parseTree(start = i+4+mopp[i+3], depth = depth+1, toffset = toffset, verbose = verbose)
            n += 4 + nsub1 + nsub2
            tris.extend(trissub1)
            tris.extend(trissub2)
            ret = True
        elif code in [0x23,0x24,0x25]: # short if x <= a then 1; if x > b then 2;
            print mopp[i+1], mopp[i+2]
            jump1 = mopp[i+3] * 256 + mopp[i+4] 
            jump2 = mopp[i+5] * 256 + mopp[i+6]
            print "  "*depth + 'if:'
            nsub1, trissub1 = self.parseTree(start = i+7+jump1, depth = depth+1, toffset = toffset, verbose = verbose)
            print "  "*depth + 'else:'
            nsub2, trissub2 = self.parseTree(start = i+7+jump2, depth = depth+1, toffset = toffset, verbose = verbose)
            n += 7 + nsub1 + nsub2
            tris.extend(trissub1)
            tris.extend(trissub2)
            ret = True
        elif code in [0x20, 0x26,0x27,0x28]:
            print mopp[i+1], mopp[i+2],
            if code == 0x26:
                print '[ bound X ]'
            elif code == 0x27:
                print '[ bound Y ]'
            elif code == 0x28:
                print '[ bound Z ]'
            else:
                print
            i += 3
            n += 3
        elif code in [0x01, 0x02, 0x03]:
            print mopp[i+1], mopp[i+2], mopp[i+3], '[ bound XYZ ]'
            i += 4
            n += 4
        #elif code in [0x00,0x01,0x02, 0x03, 0x04, 0x05, 0x06, 0x08, 0x09, 0x0C, 0x0D, 0x50, 0x53]:
        #    chunk = [code, mopp[i+1]]
        #    jump = 2
        else:
            print "unknown mopp code 0x%02X"%code
            print "following bytes are"
            extrabytes = [mopp[j] for j in xrange(i+1,min(self.moppDataSize,i+10))]
            extraindex = [j       for j in xrange(i+1,min(self.moppDataSize,i+10))]
            print extrabytes
            for b, j in zip(extrabytes, extraindex):
                if j+b+1 < self.moppDataSize:
                    print "opcode after jump %i is 0x%02X"%(b,mopp[j+b+1]), [mopp[k] for k in xrange(j+b+2,min(self.moppDataSize,j+b+11))]
            raise ValueError("unknown mopp opcode 0x%02X"%code)

    return n, tris

