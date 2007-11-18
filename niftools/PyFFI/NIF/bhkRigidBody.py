"""Custom functions for bhkRigidBody."""

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

def applyScale(self, scale):
    """Apply scale factor <scale> on data."""
    # apply scale on dimensions
    self.center.x *= scale
    self.center.y *= scale
    self.center.z *= scale

    # apply scale on all blocks down the hierarchy
    self.cls.NiObject.applyScale(self, scale)

def updateMassCenterInertia(self, density = 1):
    """Look at all the objects under this rigid body and update the mass,
    center of gravity, and inertia tensor accordingly."""
    mass, center, inertia = self.shape.getMassCenterInertia(density = density)
    self.mass = mass
    self.center.x, self.center.y, self.center.z = center
    self.inertia[0] = inertia[0][0]
    self.inertia[1] = inertia[0][1]
    self.inertia[2] = inertia[0][2]
    self.inertia[3] = 0
    self.inertia[4] = inertia[1][0]
    self.inertia[5] = inertia[1][1]
    self.inertia[6] = inertia[1][2]
    self.inertia[7] = 0
    self.inertia[8] = inertia[2][0]
    self.inertia[9] = inertia[2][1]
    self.inertia[10] = inertia[2][2]
    self.inertia[11] = 0
