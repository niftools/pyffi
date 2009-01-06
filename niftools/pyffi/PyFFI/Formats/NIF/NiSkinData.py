"""Custom functions for NiSkinData."""

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

def getTransform(self):
    """Return scale, rotation, and translation into a single 4x4 matrix."""
    mat = self.cls.Matrix44()
    mat.setScaleRotationTranslation(self.scale, self.rotation, self.translation)
    return mat

def setTransform(self, mat):
    """Set rotation, transform, and velocity."""
    scale, rotation, translation = mat.getScaleRotationTranslation()

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
    """Apply scale factor on data.

    >>> from PyFFI.Formats.NIF import NifFormat
    >>> id44 = NifFormat.Matrix44()
    >>> id44.setIdentity()
    >>> skelroot = NifFormat.NiNode()
    >>> skelroot.name = 'Scene Root'
    >>> skelroot.setTransform(id44)
    >>> bone1 = NifFormat.NiNode()
    >>> bone1.name = 'bone1'
    >>> bone1.setTransform(id44)
    >>> bone1.translation.x = 10
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
    >>> bone1.translation.x
    10.0
    >>> skindata.boneList[0].translation.x
    -10.0
    >>> skelroot.applyScale(0.1)
    >>> bone1.translation.x
    1.0
    >>> skindata.boneList[0].translation.x
    -1.0
    """

    self.translation.x *= scale
    self.translation.y *= scale
    self.translation.z *= scale

    for skindata in self.boneList:
        skindata.translation.x *= scale
        skindata.translation.y *= scale
        skindata.translation.z *= scale
        skindata.boundingSphereOffset.x *= scale
        skindata.boundingSphereOffset.y *= scale
        skindata.boundingSphereOffset.z *= scale
        skindata.boundingSphereRadius *= scale
