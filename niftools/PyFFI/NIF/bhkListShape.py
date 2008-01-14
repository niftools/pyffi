"""Custom functions for bhkListShape."""

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
# ***** END LICENCE BLOCK *****

from PyFFI.Utils.MathUtils import *

def getMassCenterInertia(self, density = 1, solid = True):
    """Return center of gravity and area."""
    subshapes_mci = [ subshape.getMassCenterInertia(density = density,
                                                    solid = solid)
                      for subshape in self.subShapes ]
    total_mass = sum(mass for mass, center, inertia in subshapes_mci)
    total_center = reduce(vecAdd,
                          ( vecscalarMul(center, mass / total_mass)
                            for mass, center, inertia in subshapes_mci ))
    total_inertia = reduce(matAdd,
                           ( inertia
                             for mass, center, inertia in subshapes_mci ))
    return total_mass, total_center, total_inertia

def addShape(self, shape, front = False):
    """Add shape to list."""
    # check if it's already there
    if shape in self.subShapes: return
    # increase number of shapes
    num_shapes = self.numSubShapes
    self.numSubShapes = num_shapes + 1
    self.subShapes.updateSize()
    # add the shape
    if not front:
        self.subShapes[num_shapes] = shape
    else:
        for i in xrange(num_shapes, 0, -1):
            self.subShapes[i] = self.subShapes[i-1]
        self.subShapes[0] = shape
    # expand list of unknown ints as well
    self.numUnknownInts = num_shapes + 1
    self.unknownInts.updateSize()

def removeShape(self, shape):
    """Remove a shape from the shape list."""
    # get list of shapes excluding the shape to remove
    shapes = [s for s in self.subShapes if s != shape]
    # set subShapes to this list
    self.numSubShapes = len(shapes)
    self.subShapes.updateSize()
    for i, s in enumerate(shapes):
        self.subShapes[i] = s
    # update unknown ints
    self.numUnknownInts = len(shapes)
    self.unknownInts.updateSize()
