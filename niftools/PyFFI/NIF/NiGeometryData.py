# --------------------------------------------------------------------------
# NifFormat.NiGeometryData
# Custom functions for NiGeometryData.
# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------

def updateCenterRadius(self):
    """Recalculate center and radius of the data."""
    # in case there are no vertices, set center and radius to zero
    if len(self.vertices) == 0:
        self.center.x = 0.0
        self.center.y = 0.0
        self.center.z = 0.0
        self.radius = 0.0
        return

    # find extreme values in x, y, and z direction
    lowx = min([v.x for v in self.vertices])
    lowy = min([v.y for v in self.vertices])
    lowz = min([v.z for v in self.vertices])
    highx = max([v.x for v in self.vertices])
    highy = max([v.y for v in self.vertices])
    highz = max([v.z for v in self.vertices])

    # center is in the center of the bounding box
    cx = (lowx + highx) * 0.5
    cy = (lowy + highy) * 0.5
    cz = (lowz + highz) * 0.5
    self.center.x = cx
    self.center.y = cy
    self.center.z = cz

    # radius is the largest distance from the center
    r2 = 0.0
    for v in self.vertices:
        dx = cx - v.x
        dy = cy - v.y
        dz = cz - v.z
        r2 = max(r2, dx*dx+dy*dy+dz*dz)
    self.radius = r2 ** 0.5

def applyScale(self, scale):
    """Apply scale factor on data."""
    if abs(scale - 1.0) < self.cls._EPSILON: return
    for v in self.vertices:
        v.x *= scale
        v.y *= scale
        v.z *= scale
    self.center.x *= scale
    self.center.y *= scale
    self.center.z *= scale
    self.radius *= scale
