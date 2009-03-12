"""Custom functions for ControllerLink.

>>> # a doctest
>>> from PyFFI.Formats.NIF import NifFormat
>>> link = NifFormat.ControllerLink()
>>> link.nodeNameOffset
-1
>>> link.setNodeName("Bip01")
>>> link.nodeNameOffset
0
>>> link.getNodeName()
'Bip01'
>>> link.nodeName
'Bip01'
>>> link.setNodeName("Bip01 Tail")
>>> link.nodeNameOffset
6
>>> link.getNodeName()
'Bip01 Tail'
>>> link.nodeName
'Bip01 Tail'
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

def _getString(self, offset):
    """A wrapper around stringPalette.palette.getString. Used by getNodeName
    etc. Returns the string at given offset."""
    if offset == -1:
        return ''

    if not self.stringPalette:
        return ''

    return self.stringPalette.palette.getString(offset)

def _addString(self, text):
    """Wrapper for stringPalette.palette.addString. Used by setNodeName etc.
    Returns offset of string added."""
    # create string palette if none exists yet
    if not self.stringPalette:
        self.stringPalette = self.cls.NiStringPalette()
    # add the string and return the offset
    return self.stringPalette.palette.addString(text)

def getNodeName(self):
    """Return the node name.

    >>> # a doctest
    >>> from PyFFI.Formats.NIF import NifFormat
    >>> link = NifFormat.ControllerLink()
    >>> link.stringPalette = NifFormat.NiStringPalette()
    >>> palette = link.stringPalette.palette
    >>> link.nodeNameOffset = palette.addString("Bip01")
    >>> link.getNodeName()
    'Bip01'

    >>> # another doctest
    >>> from PyFFI.Formats.NIF import NifFormat
    >>> link = NifFormat.ControllerLink()
    >>> link.nodeName = "Bip01"
    >>> link.getNodeName()
    'Bip01'
    """
    if self.nodeName:
        return self.nodeName
    else:
        return self._getString(self.nodeNameOffset)

def setNodeName(self, text):
    self.nodeName = text
    self.nodeNameOffset = self._addString(text)

def getPropertyType(self):
    if self.propertyType:
        return self.propertyType
    else:
        return self._getString(self.propertyTypeOffset)

def setPropertyType(self, text):
    self.propertyType = text
    self.propertyTypeOffset = self._addString(text)

def getControllerType(self):
    if self.controllerType:
        return self.controllerType
    else:
        return self._getString(self.controllerTypeOffset)

def setControllerType(self, text):
    self.controllerType = text
    self.controllerTypeOffset = self._addString(text)

def getVariable1(self):
    if self.variable1:
        return self.variable1
    else:
        return self._getString(self.variable1Offset)

def setVariable1(self, text):
    self.variable1 = text
    self.variable1Offset = self._addString(text)

def getVariable2(self):
    if self.variable2:
        return self.variable2
    else:
        return self._getString(self.variable2Offset)

def setVariable2(self, text):
    self.variable2 = text
    self.variable2Offset = self._addString(text)
