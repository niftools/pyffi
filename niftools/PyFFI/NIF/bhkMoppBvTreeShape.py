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

def update(self):
    """Update scale, origin, and mopp data."""

    self.updateOriginScale()
    self.updateTree()

# ported from NifVis/bhkMoppBvTreeShape.py
def _getSubTree(self, start, length):
    """Get a mopp subtree (for internal purposes only)."""
    mopp = self.moppData
    tree = []
    i = start
    end = start + length
    while i < end:
        code = mopp[i]
        if code >= 0x30:
            chunk = [code]
            jump = 1
        elif code in xrange(0x10, 0x20):
            subsize = mopp[i+3]
            subtree = self._getSubTree(i+4, subsize)
            chunk = [code, mopp[i+1], mopp[i+2], subtree]
            jump = 4+subsize
        else:
            chunk = [code, mopp[i+1], mopp[i+2]]
            jump = 3
        #else:
        #    raise ValueError("unknown mopp opcode 0x%X"%code)
        tree.append(chunk)
        i += jump
    return tree

def getTree(self):
    return self._getSubTree(0, self.moppDataSize)

def _printSubTree(self, chunk, depth = 0):
    """Print a mopp subtree (for internal purposes only)."""
    code = chunk[0]
    print "  "*depth + '0x%02X'%code,
    if code >= 0x30:
        print
    else:
        print chunk[1], chunk[2]
        if code in xrange(0x10, 0x20): # chunk[3] is subtree
            for subchunk in chunk[3]:
                self._printSubTree(subchunk, depth+1)

def printTree(self):
    """Print the mopp tree."""
    for chunk in self.getTree():
        self._printSubTree(chunk)
