"""Custom functions for NiSkinData."""

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

from PyFFI.Utils.MathUtils import LMatrix

def getTransform(self):
    """Return scale, rotation, and translation into a single 4x4 matrix."""
    return LMatrix.composeScaleRotationTranslation(
        Vector(self.scale, self.scale, self.scale),
        self.rotation, self.translation)

def setTransform(self, mat):
    """Set rotation, transform, and velocity."""
    scale, self.rotation = mat.getScaleRotation(conformal = True)
    self.scale = sum(scale) / 3.0
    self.translation = mat.getTranslation()
    
def applyScale(self, scale):
    """Apply scale factor on data.

    >>> from PyFFI.NIF import NifFormat
    >>> from PyFFI.Utils.MathUtils import LMatrix
    >>> id44 = LMatrix.getIdentity(4, 4, affine = True)
    >>> skelroot = NifFormat.NiNode()
    >>> skelroot.name = 'Scene Root'
    >>> skelroot.setTransform(id44)
    >>> bone1 = NifFormat.NiNode()
    >>> bone1.name = 'bone1'
    >>> bone1.setTransform(id44)
    >>> bone1.translation = (10.0, 0, 0)
    >>> skelroot.addChild(bone1)
    >>> geom = NifFormat.NiTriShape()
    >>> geom.setTransform(id44)
    >>> skelroot.addChild(geom)
    >>> skininst = NifFormat.NiSkinInstance()
    >>> geom.skinInstance = skininst
    >>> skininst.skeletonRoot = skelroot
    >>> skindata = NifFormat.NiSkinData()
    >>> skininst.data = skindata
    >>> skindata.setTransform(id44)
    >>> geom.addBone(bone1, {})
    >>> geom.updateBindPosition()
    >>> bone1.translation[0]
    10.0
    >>> skindata.boneList[0].translation[0]
    -10.0
    >>> skelroot.applyScale(0.1)
    >>> bone1.translation[0]
    1.0
    >>> skindata.boneList[0].translation[0]
    -1.0
    """

    self.translation *= scale

    for skindata in self.boneList:
        skindata.translation *= scale
        skindata.boundingSphereOffset *= scale
        skindata.boundingSphereRadius *= scale
