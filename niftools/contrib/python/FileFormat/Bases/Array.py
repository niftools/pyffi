# --------------------------------------------------------------------------
# FileFormat.Bases.Array
# Implements class for arrays.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
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
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

from Basic import BasicBase

class Array(object):
    # initialize the array
    def __init__(self, element_type, element_type_template, count):
        self._elements = []
        self._elementType = element_type
        self._elementTypeTemplate = element_type_template
        self._count = count
        
        for i in xrange(self._count):
            self._elements.append(self._elementType())

        if issubclass(self._elementType, BasicBase):
            self.__getitem__ = self.getBasicItem
            self.__setitem__ = self.setBasicItem
        else:
            self.__getitem__ = self.getItem

    # string of the array
    def __str__(self):
        s = '%s instance at 0x%08X\n'%(self.__class__, id(self))
        for i, element in enumerate(self._elements):
            s += "%i: %s\n"%(i, element)
        return s

    def getBasicItem(self, index):
        return self._elements[index].getValue()

    def setBasicItem(self, index, value):
        return self._elements[index].setValue(value)

    def getItem(self, index):
        return self._elements[index]
