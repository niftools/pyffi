# --------------------------------------------------------------------------
# NifFormat.NiAVObject
# Custom functions for NiAVObject.
# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------

def addProperty(self, propblock):
    """Add block to property list."""
    num_props = self.numProperties
    self.numProperties = num_props + 1
    self.properties.updateSize()
    self.properties[num_props] = propblock

def getTransform(self, relative_to = None):
    """Return scale, rotation, and translation into a single 4x4 matrix,
    relative to the <relative_to> block (which should be another NiAVObject
    connecting to this block). If <relative_to> == None, then returns the
    transform stored in self, or equivalently, the target is assumed to be the
    parent."""
    m = self.cls.Matrix44()
    m.setScaleRotationTranslation(self.scale, self.rotation, self.translation)
    if relative_to == None: return m
    # find chain from relative_to to self
    chain = relative_to.findChain(self, block_type = self.cls.NiAVObject)
    if not chain:
        raise ValueError('cannot find a chain of NiAVObject blocks')
    # and multiply with all transform matrices (not including relative_to)
    for block in reversed(chain[1:-1]):
        m *= block.getTransform()
    return m

def setTransform(self, m):
    """Set rotation, transform, and velocity."""
    scale, rotation, translation = m.getScaleRotationTranslation()

    self.scale = scale
    
    self.rotation.m11 = rotation.m11
    self.rotation.m12 = rotation.m12
    self.rotation.m13 = rotation.m13
    self.rotation.m21 = rotation.m21
    self.rotation.m22 = rotation.m22
    self.rotation.m23 = rotation.m23
    self.rotation.m31 = rotation.m31
    self.rotation.m32 = rotation.m32
    self.rotation.m33 = rotation.m33
    
    self.translation.x = translation.x
    self.translation.y = translation.y
    self.translation.z = translation.z
    
def applyScale(self, scale):
    """Apply scale factor <scale> on data."""
    # apply scale on translation
    self.translation.x *= scale
    self.translation.y *= scale
    self.translation.z *= scale
    # apply scale on bounding box
    self.boundingBox.translation.x *= scale
    self.boundingBox.translation.y *= scale
    self.boundingBox.translation.z *= scale
    self.boundingBox.radius.x *= scale
    self.boundingBox.radius.y *= scale
    self.boundingBox.radius.z *= scale

    # apply scale on all blocks down the hierarchy
    self.cls.NiObject.applyScale(self, scale)
