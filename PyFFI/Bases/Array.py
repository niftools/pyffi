# --------------------------------------------------------------------------
# PyFFI.Bases.Array
# Implements class for arrays.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, Python File Format Interface
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
#    * Neither the name of the Python File Format Interface
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
from Expression import Expression

class _ListWrap(list):
    """A wrapper for list, which uses getValue and setValue for
    getting and setting items of the basic type."""
    def __init__(self, element_type):
        list.__init__(self)
        if issubclass(element_type, BasicBase):
            self._getitem_hook = self.getBasicItem
            self._setitem_hook = self.setBasicItem
            self._iteritem_hook = self.iterBasicItem
        else:
            self._getitem_hook = self.getItem
            self._setitem_hook = self._notimplemented_hook
            self._iteritem_hook = self.iterItem

    def __getitem__(self, index):
        return self._getitem_hook(index)

    def __setitem__(self, index, value):
        return self._setitem_hook(index, value)

    def __iter__(self):
        return self._iteritem_hook()

    def _notimplemented_hook(self, *args):
        raise NotImplementedError

    def iterBasicItem(self):
        for e in list.__iter__(self):
            yield e.getValue()

    def iterItem(self):
        for e in list.__iter__(self):
            yield e

    def getBasicItem(self, index):
        return list.__getitem__(self, index).getValue()

    def setBasicItem(self, index, value):
        return list.__getitem__(self, index).setValue(value)

    def getItem(self, index):
        return list.__getitem__(self, index)

class Array(_ListWrap):
    # initialize the array
    def __init__(self, parent, element_type, element_type_template, element_type_argument, count1, count2 = None):
        if count2 == None:
            _ListWrap.__init__(self, element_type)
        else:
            _ListWrap.__init__(self, _ListWrap)
        self._elementType = element_type
        self._parent = parent
        self._elementTypeTemplate = element_type_template
        self._elementTypeArgument = element_type_argument
        self._count1 = count1
        self._count2 = count2
        
        if self._count2 == None:
            for i in xrange(self._len1()):
                self.append(self._elementType(self._elementTypeTemplate, self._elementTypeArgument))
        else:
            for i in xrange(self._len1()):
                el = _ListWrap(element_type)
                for j in xrange(self._len2(i)):
                    el.append(self._elementType(self._elementTypeTemplate, self._elementTypeArgument))
                self.append(el)

    def _len1(self):
        """The length the array *should* have, obtained by evaluating
        the count1 expression."""
	return self._count1.eval(self._parent)

    def _len2(self, index1):
        """The length the array *should* have, obtained by evaluating
        the count2 expression."""
        if self._count2 == None:
            raise ValueError('single array treated as double array (bug?)')
        e = self._count2.eval(self._parent)
        #if isinstance(e, BasicBase):
        #    return e.getValue()
        if isinstance(e, (int, long)):
            return e
        else:
            return e[index1]

    # string of the array
    def __str__(self):
        s = '%s instance at 0x%08X\n'%(self.__class__, id(self))
        if self._count2 == None:
            for i, element in enumerate(list.__iter__(self)):
                if i > 16:
                    s += "etc...\n"
                    break
                s += "%i: %s\n"%(i, element)
        else:
            k = 0
            for i, el in enumerate(list.__iter__(self)):
                for j, e in enumerate(list.__iter__(el)):
                    if k > 16:
                        s += "etc...\n"
                        break
                    s += "%i, %i: %s\n"%(i, j, e)
                    k += 1
                if k > 16: break
        return s

    def updateSize(self):
        old_size = len(self)
        new_size = self._len1()
        if self._count2 == None:
            if new_size < old_size:
                self.__delslice__(new_size, old_size)
            else:
                for i in xrange(new_size-old_size):
                    e = self._elementType(self._elementTypeTemplate, self._elementTypeArgument)
                    self.append(e)
        else:
            if new_size < old_size:
                self.__delslice__(new_size, old_size)
            else:
                for i in xrange(new_size-old_size):
                    self.append(_ListWrap(self._elementType))
            for i, el in enumerate(list.__iter__(self)):
                old_size_i = len(el)
                new_size_i = self._len2(i)
                if new_size_i < old_size_i:
                    el.__delslice__(new_size_i, old_size_i)
                else:
                    for j in xrange(new_size_i-old_size_i):
                        e = self._elementType(self._elementTypeTemplate, self._elementTypeArgument)
                        el.append(e)

    def read(self, version, user_version, f, link_stack, string_list, argument):
        len1 = self._len1()
        if len1 > 1000000: raise ValueError('array too long')
        self._elementTypeArgument = argument
        self.__delslice__(0, self.__len__())
        if self._count2 == None:
            for i in xrange(len1):
                e = self._elementType(self._elementTypeTemplate, self._elementTypeArgument)
                e.read(version, user_version, f, link_stack, string_list, self._elementTypeArgument)
                self.append(e)
        else:
            for i in xrange(len1):
                len2i = self._len2(i)
                if len2i > 1000000: raise ValueError('array too long')
                el = _ListWrap(self._elementType)
                for j in xrange(len2i):
                    e = self._elementType(self._elementTypeTemplate, self._elementTypeArgument)
                    e.read(version, user_version, f, link_stack, string_list, self._elementTypeArgument)
                    el.append(e)
                self.append(el)

    def write(self, version, user_version, f, block_index_dct, string_list, arg):
        len1 = self._len1()
        if len1 != self.__len__():
            raise ValueError('array size (%i) different from to field describing number of elements (%i)'%(self.__len__(),len1))
        if len1 > 1000000: raise ValueError('array too long (%i)'%len1)
        if self._count2 == None:
            for e in list.__iter__(self):
                e.write(version, user_version, f, block_index_dct, string_list, self._elementTypeArgument)
        else:
            for i, el in enumerate(list.__iter__(self)):
                len2i = self._len2(i)
                if len2i != el.__len__():
                    raise ValueError('array size (%i) different from to field describing number of elements (%i)'%(el.__len__(),len2i))
                if len2i > 1000000: raise ValueError('array too long (%i)'%len2i)
                for e in list.__iter__(el):
                    e.write(version, user_version, f, block_index_dct, string_list, self._elementTypeArgument)

    def fixLinks(self, version, user_version, block_dct, link_stack):
        if not self._elementType._hasLinks: return
        if self._count2 == None:
            for e in list.__iter__(self):
                e.fixLinks(version, user_version, block_dct, link_stack)
        else:
            for el in list.__iter__(self):
                for e in list.__iter__(el):
                    e.fixLinks(version, user_version, block_dct, link_stack)

    def getLinks(self, version, user_version):
        links = []
        if not self._elementType._hasLinks: return links
        if self._count2 == None:
            for e in list.__iter__(self):
                links.extend(e.getLinks(version, user_version))
        else:
            for el in list.__iter__(self):
                for e in list.__iter__(el):
                    links.extend(e.getLinks(version, user_version))
        return links

    def getStrings(self, version, user_version):
        strings = []
        if not self._elementType._hasStrings: return strings
        if self._count2 == None:
            for e in list.__iter__(self):
                strings.extend(e.getStrings(version, user_version))
        else:
            for el in list.__iter__(self):
                for e in list.__iter__(el):
                    strings.extend(e.getStrings(version, user_version))
        return strings

    def getRefs(self):
        links = []
        if not self._elementType._hasLinks: return links
        if self._count2 == None:
            for e in list.__iter__(self):
                links.extend(e.getRefs())
        else:
            for el in list.__iter__(self):
                for e in list.__iter__(el):
                    links.extend(e.getRefs())
        return links
