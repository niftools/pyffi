"""Custom functions for ControllerLink.

>>> from PyFFI.NIF import NifFormat
>>> link = NifFormat.ControllerLink()
>>> link.stringPalette = NifFormat.NiStringPalette()
>>> palette = link.stringPalette.stringPalette
>>> link.nodeNameOffset = palette.addString("Bip01")
>>> link.controllerTypeOffset = palette.addString("NiTransformController")
>>> print link.getNodeName()
>>> print link.getControllerType()
"""

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

def _getString(self, offset):
    """A wrapper around stringPalette.getString. Used by getNodeName etc."""
    if not self.stringPalette:
        return ''

    if offset == -1:
        return ''

    return self.stringPalette.stringPalette.getString(offset)

def _addString(self, text):
    """Wrapper for stringPalette.addString. Used by setNodeName etc. Returns
    offset of string added."""
    if not self.stringPalette:
        self.stringPalette = self.cls.NiStringPalette()
    self.stringPalette.stringPalette.addString(text)

def getNodeName(self):
    if self.nodeName:
        return self.nodeName
    else:
        return self._getString(self.nodeNameOffset)

def setNodeName(self, text):
    self.nodeName = text
    self.stringPalette

def getPropertyType(self):
    if self.propertyType:
        return self.propertyType
    else:
        return self._getString(self.propertyTypeOffset)

def getControllerType(self):
    if self.controllerType:
        return self.controllerType
    else:
        return self._getString(self.controllerTypeOffset)

def getVariable1(self):
    if self.variable1:
        return self.variable1
    else:
        return self._getString(self.variable1Offset)

def getVariable2(self):
    if self.variable2:
        return self.variable2
    else:
        return self._getString(self.variable2Offset)
