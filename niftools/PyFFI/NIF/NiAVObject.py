"""Custom functions for NiAVObject."""

# ***** BEGIN LICENCE BLOCK *****
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
# ***** END LICENSE BLOCK *****

from PyFFI.Utils.MathUtils import Vector, LMatrix

def addProperty(self, propblock):
    """Add block C{propblock} to property list.

    @param propblock: The property block to add."""
    num_props = self.numProperties
    self.numProperties = num_props + 1
    self.properties.updateSize()
    self.properties[num_props] = propblock

def getTransform(self, relative_to = None):
    """Return scale, rotation, and translation into a single 4x4 matrix,
    relative to the C{relative_to} block (which should be another NiAVObject
    connecting to this block). If C{relative_to} is C{None}, then returns the
    transform stored in C{self}, or equivalently, the target is assumed to be the
    parent.

    @param relative_to: The block relative to which the transform must be calculated. If C{None}, the local transform is returned."""
    mat = LMatrix.composeScaleRotationTranslation(Vector(self.scale, self.scale, self.scale), self.rotation, self.translation)
    if not relative_to:
        return mat
    # find chain from relative_to to self
    chain = relative_to.findChain(self, block_type = self.cls.NiAVObject)
    if not chain:
        raise ValueError('cannot find a chain of NiAVObject blocks')
    # and multiply with all transform matrices (not including relative_to)
    for block in reversed(chain[1:-1]):
        mat *= block.getTransform()
    return mat

def setTransform(self, mat):
    """Set rotation, translation, and scale, from a transform matrix.

    @param mat: The matrix to which the transform should be set."""
    if not (mat._dim_n == 4 and mat._dim_m == 4 and mat._affine):
        raise ValueError("expected affine 4x4 matrix but got %s %ix%i matrix"
                         % ("affine" if mat._affine else "non-affine",
                            mat._dim_n, mat._dim_m))
    scale, self.rotation = mat.getScaleRotation(conformal = True)
    self.scale = scale[0]
    self.translation = mat.getTranslation()
    
def applyScale(self, scale):
    """Apply scale factor on data.

    @param scale: The scale factor."""
    # apply scale on translation
    self.translation *= scale
    # apply scale on bounding box
    self.boundingBox.translation *= scale
    self.boundingBox.radius *= scale

    # apply scale on all blocks down the hierarchy
    self.cls.NiObject.applyScale(self, scale)
