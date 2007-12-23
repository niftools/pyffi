"""Custom functions for bhkBoxShape."""

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

from PyFFI.Utils import Inertia

def applyScale(self, scale):
    """Apply scale factor C{scale} on data."""
    # apply scale on dimensions
    self.dimensions.x *= scale
    self.dimensions.y *= scale
    self.dimensions.z *= scale
    self.minimumSize  *= scale

    # apply scale on all blocks down the hierarchy
    self.cls.NiObject.applyScale(self, scale)

def getMassCenterInertia(self, density = 1, solid = True):
    """Return mass, center, and inertia tensor."""
    # the dimensions describe half the size of the box in each dimension
    # so the length of a single edge is dimension.dir * 2
    mass, inertia = Inertia.getMassInertiaBox(
        (self.dimensions.x * 2, self.dimensions.y * 2, self.dimensions.z * 2),
        density = density, solid = solid)
    return mass, (0,0,0), inertia
