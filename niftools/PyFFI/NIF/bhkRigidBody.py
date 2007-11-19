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

    self.inertia[0] *= (scale ** 2)
    self.inertia[1] *= (scale ** 2)
    self.inertia[2] *= (scale ** 2)
    self.inertia[3] *= (scale ** 2)
    self.inertia[4] *= (scale ** 2)
    self.inertia[5] *= (scale ** 2)
    self.inertia[6] *= (scale ** 2)
    self.inertia[7] *= (scale ** 2)
    self.inertia[8] *= (scale ** 2)
    self.inertia[9] *= (scale ** 2)
    self.inertia[10] *= (scale ** 2)
    self.inertia[11] *= (scale ** 2)

    # apply scale on all blocks down the hierarchy
    self.cls.NiObject.applyScale(self, scale)

def updateMassCenterInertia(self, density = 1, solid = True, mass = None):
    """Look at all the objects under this rigid body and update the mass,
    center of gravity, and inertia tensor accordingly. If the C{mass} parameter
    is given then the C{density} argument is ignored."""
    if not mass is None:
        density = 1
    
    calc_mass, center, inertia = self.shape.getMassCenterInertia(
        density = density, solid = solid)

    self.mass = calc_mass
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

    if not mass is None:
        mass_correction = mass / calc_mass if calc_mass != 0 else 1
        self.mass = mass
        self.inertia[0] *= mass_correction
        self.inertia[1] *= mass_correction
        self.inertia[2] *= mass_correction
        self.inertia[3] *= mass_correction
        self.inertia[4] *= mass_correction
        self.inertia[5] *= mass_correction
        self.inertia[6] *= mass_correction
        self.inertia[7] *= mass_correction
        self.inertia[8] *= mass_correction
        self.inertia[9] *= mass_correction
        self.inertia[10] *= mass_correction
        self.inertia[11] *= mass_correction
