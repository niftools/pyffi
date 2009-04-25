"""Custom functions for NiAVObject.

Properties
==========

>>> from PyFFI.Formats.NIF import NifFormat
>>> node = NifFormat.NiNode()
>>> prop1 = NifFormat.NiProperty()
>>> prop1.name = "hello"
>>> prop2 = NifFormat.NiProperty()
>>> prop2.name = "world"
>>> node.getProperties()
[]
>>> node.setProperties([prop1, prop2])
>>> [prop.name for prop in node.getProperties()]
['hello', 'world']
>>> [prop.name for prop in node.properties]
['hello', 'world']
>>> node.setProperties([])
>>> node.getProperties()
[]
>>> # now set them the other way around
>>> node.setProperties([prop2, prop1])
>>> [prop.name for prop in node.getProperties()]
['world', 'hello']
>>> [prop.name for prop in node.properties]
['world', 'hello']
>>> node.removeProperty(prop2)
>>> [prop.name for prop in node.properties]
['hello']
>>> node.addProperty(prop2)
>>> [prop.name for prop in node.properties]
['hello', 'world']
"""

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

def addProperty(self, prop):
    """Add the given property to the property list.

    :param prop: The property block to add.
    :type prop: L{NifFormat.NiProperty}
    """
    num_props = self.numProperties
    self.numProperties = num_props + 1
    self.properties.updateSize()
    self.properties[num_props] = prop

def removeProperty(self, prop):
    """Remove the given property to the property list.

    :param prop: The property block to remove.
    :type prop: L{NifFormat.NiProperty}
    """
    self.setProperties([otherprop for otherprop in self.getProperties()
                        if not(otherprop is prop)])

def getProperties(self):
    """Return a list of the properties of the block.

    :return: The list of properties.
    :rtype: C{list} of L{NifFormat.NiProperty}
    """
    return [prop for prop in self.properties]

def setProperties(self, proplist):
    """Set the list of properties from the given list (destroys existing list).

    :param proplist: The list of property blocks to set.
    :type proplist: C{list} of L{NifFormat.NiProperty}
    """
    self.numProperties = len(proplist)
    self.properties.updateSize()
    for i, prop in enumerate(proplist):
        self.properties[i] = prop

def getTransform(self, relative_to=None):
    """Return scale, rotation, and translation into a single 4x4
    matrix, relative to the C{relative_to} block (which should be
    another NiAVObject connecting to this block). If C{relative_to} is
    ``None``, then returns the transform stored in C{self}, or
    equivalently, the target is assumed to be the parent.

    :param relative_to: The block relative to which the transform must
        be calculated. If ``None``, the local transform is returned.
    """
    m = self.cls.Matrix44()
    m.setScaleRotationTranslation(self.scale, self.rotation, self.translation)
    if not relative_to: return m
    # find chain from relative_to to self
    chain = relative_to.findChain(self, block_type = self.cls.NiAVObject)
    if not chain:
        raise ValueError('cannot find a chain of NiAVObject blocks')
    # and multiply with all transform matrices (not including relative_to)
    for block in reversed(chain[1:-1]):
        m *= block.getTransform()
    return m

def setTransform(self, m):
    """Set rotation, translation, and scale, from a 4x4 matrix.

    :param m: The matrix to which the transform should be set."""
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
    """Apply scale factor on data.

    :param scale: The scale factor."""
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
