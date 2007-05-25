# --------------------------------------------------------------------------
# NifFormat.NiTriStripsData
# Custom functions for NiTriStripsData.
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

from FileFormat.Bases.Array import Array
from FileFormat.Bases.Expression import Expression
from PyTriStrip import PyTriStrip

def generateFaces(self):
    for strip in self.points:
        for face in PyTriStrip.generateFaces(strip):
            yield face

def setFaces(self, faces):
    strips = PyTriStrip.getStrips(faces)
    self.numStrips = len(strips)
    self.stripLengths.updateSize()
    for i, strip in enumerate(strips):
        self.stripLengths[i] = len(strip)
    self.points.updateSize()
    for i, strip in enumerate(strips):
        for j, idx in enumerate(strip):
            self.points[i][j] = idx

# use generateFaces
def _get_triangles(self):
    """Get list of all triangles in all strips."""
    raise NotImplementedError('use generateFaces()')

def _set_triangles(self):
    """Construct strips from triangles."""
    raise NotImplementedError('use setFaces()')
