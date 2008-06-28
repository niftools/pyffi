"""Custom functions for NiTriShapeData.

Example usage:
>>> from PyFFI.Formats.NIF import NifFormat
>>> block = NifFormat.NiTriShapeData()
>>> block.setTriangles([(0,1,2),(2,1,3),(2,3,4)])
>>> block.getStrips()
[[4, 4, 3, 2, 1, 0]]
>>> block.getTriangles()
[(0, 1, 2), (2, 1, 3), (2, 3, 4)]
>>> block.setStrips([[1,0,1,2,3,4]])
>>> block.getStrips()
[[0, 0, 1, 2, 3, 4]]
>>> block.getTriangles()
[(0, 2, 1), (1, 2, 3), (2, 4, 3)]
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
# ***** END LICENSE BLOCK *****

from PyFFI.Utils import TriStrip

def getTriangles(self):
    return [(t.v1, t.v2, t.v3) for t in self.triangles]

def setTriangles(self, triangles, stitchstrips = False):
    # note: the stitchstrips argument is ignored - only present to ensure
    # uniform interface between NiTriShapeData and NiTriStripsData

    # initialize triangle array
    n = len(triangles)
    self.numTriangles = n
    self.numTrianglePoints = 3*n
    self.hasTriangles = (n > 0)
    self.triangles.updateSize()

    # copy triangles
    src = triangles.__iter__()
    dst = self.triangles.__iter__()
    for k in xrange(n):
        dst_t = dst.next()
        dst_t.v1, dst_t.v2, dst_t.v3 = src.next()

def getStrips(self):
    return TriStrip.stripify(self.getTriangles())

def setStrips(self, strips):
    self.setTriangles(TriStrip.triangulate(strips))
