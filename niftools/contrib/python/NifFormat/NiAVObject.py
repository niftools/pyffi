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

def _get_transform(self, cls):
    """Compose transforms into a single 4x4 matrix."""
    m = cls.Matrix44()

    # maybe port this "algorithm" to the Matrix44 class?
    
    m.m11 = self.rotation.m11 * self.scale
    m.m12 = self.rotation.m12 * self.scale
    m.m13 = self.rotation.m13 * self.scale
    m.m21 = self.rotation.m21 * self.scale
    m.m22 = self.rotation.m22 * self.scale
    m.m23 = self.rotation.m23 * self.scale
    m.m31 = self.rotation.m31 * self.scale
    m.m32 = self.rotation.m32 * self.scale
    m.m33 = self.rotation.m33 * self.scale
    
    # should be all zero, but for the sake of mathematical rigour...
    m.m14 = self.velocity.x * self.scale
    m.m24 = self.velocity.y * self.scale
    m.m34 = self.velocity.z * self.scale
    
    m.m41 = self.translation.x
    m.m42 = self.translation.y
    m.m43 = self.translation.z
    
    m.m44 = 1.0
    
    return m

def _set_transform(self, cls, m):
    """Set rotation, transform, and velocity."""
    raise NotImplementedError
