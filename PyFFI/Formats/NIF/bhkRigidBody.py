"""Custom functions for bhkRigidBody."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, NIF File Format Library and Tools.
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
    # apply scale on transform
    self.translation.x *= scale
    self.translation.y *= scale
    self.translation.z *= scale

    # apply scale on center of gravity
    self.center.x *= scale
    self.center.y *= scale
    self.center.z *= scale

    # apply scale on inertia tensor
    self.inertia.m11 *= (scale ** 2)
    self.inertia.m12 *= (scale ** 2)
    self.inertia.m13 *= (scale ** 2)
    self.inertia.m14 *= (scale ** 2)
    self.inertia.m21 *= (scale ** 2)
    self.inertia.m22 *= (scale ** 2)
    self.inertia.m23 *= (scale ** 2)
    self.inertia.m24 *= (scale ** 2)
    self.inertia.m31 *= (scale ** 2)
    self.inertia.m32 *= (scale ** 2)
    self.inertia.m33 *= (scale ** 2)
    self.inertia.m34 *= (scale ** 2)

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
    self.inertia.m11 = inertia[0][0]
    self.inertia.m12 = inertia[0][1]
    self.inertia.m13 = inertia[0][2]
    self.inertia.m14 = 0
    self.inertia.m21 = inertia[1][0]
    self.inertia.m22 = inertia[1][1]
    self.inertia.m23 = inertia[1][2]
    self.inertia.m24 = 0
    self.inertia.m31 = inertia[2][0]
    self.inertia.m32 = inertia[2][1]
    self.inertia.m33 = inertia[2][2]
    self.inertia.m34 = 0

    if not mass is None:
        mass_correction = mass / calc_mass if calc_mass != 0 else 1
        self.mass = mass
        self.inertia.m11 *= mass_correction
        self.inertia.m12 *= mass_correction
        self.inertia.m13 *= mass_correction
        self.inertia.m14 *= mass_correction
        self.inertia.m21 *= mass_correction
        self.inertia.m22 *= mass_correction
        self.inertia.m23 *= mass_correction
        self.inertia.m24 *= mass_correction
        self.inertia.m31 *= mass_correction
        self.inertia.m32 *= mass_correction
        self.inertia.m33 *= mass_correction
        self.inertia.m34 *= mass_correction
