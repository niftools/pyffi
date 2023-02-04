"""
:mod:`pyffi.object_models.xml.array` --- Array classes
==============================================================

Implements class for arrays.

Implementation
--------------

.. autoclass:: Array
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: _ListWrap
   :show-inheritance:
   :members:
   :undoc-members:

.. todo:: Show examples for usage
"""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface
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
# ***** END LICENSE BLOCK *****
# --------------------------------------------------------------------------

# note: some imports are defined at the end to avoid problems with circularity

import logging
import weakref
from typing import Optional

from object_models.expression import Expression
from pyffi.object_models.basic import BasicBase
from pyffi.utils.graph import DetailNode, EdgeFilter


class _ListWrap(list, DetailNode):
    """A wrapper for list, which uses get_value and set_value for
    getting and setting items of the basic type."""

    def __init__(self, element_type, parent=None):
        self._parent = weakref.ref(parent) if parent else None
        self._elementType = element_type
        # we link to the unbound methods (that is, self.__class__.xxx
        # instead of self.xxx) to avoid circular references!!
        if issubclass(element_type, BasicBase):
            self._get_item_hook = self.__class__.get_basic_item
            self._set_item_hook = self.__class__.set_basic_item
            self._iter_item_hook = self.__class__.iter_basic_item
        else:
            self._get_item_hook = self.__class__.get_item
            self._set_item_hook = self.__class__.set_item  # TODO: Why should this work?
            self._iter_item_hook = self.__class__.iter_item

    def __getitem__(self, index):
        return self._get_item_hook(self, index)

    def __setitem__(self, index, value):
        return self._set_item_hook(self, index, value)

    def __iter__(self):
        return self._iter_item_hook(self)

    def __contains__(self, value):
        # ensure that the "in" operator uses self.__iter__() rather than
        # list.__iter__()
        for elem in self.__iter__():
            if elem == value:
                return True
        return False

    def _not_implemented_hook(self, *args):
        """A hook for members that are not implemented."""
        raise NotImplementedError

    def iter_basic_item(self):
        """Iterator which calls C{get_value()} on all items. Applies when
        the list has BasicBase elements."""
        for elem in list.__iter__(self):
            yield elem.get_value()

    def iter_item(self):
        """Iterator over all items. Applies when the list does not have
        BasicBase elements."""
        for elem in list.__iter__(self):
            yield elem

    def get_basic_item(self, index):
        """Item getter which calls C{get_value()} on the C{index}'d item."""
        return list.__getitem__(self, index).get_value()

    def set_basic_item(self, index, value):
        """Item setter which calls C{set_value()} on the C{index}'d item."""
        return list.__getitem__(self, index).set_value(value)

    def get_item(self, index):
        """Regular item getter, used when the list does not have BasicBase
        elements."""
        return list.__getitem__(self, index)

    def set_item(self, index, value):
        """Regular item setter, used when the list does not have BasicBase
        elements."""
        return list.__setitem__(self, index, value)

    # DetailNode

    def get_detail_child_nodes(self, edge_filter=EdgeFilter()):
        """Yield children."""
        return (item for item in list.__iter__(self))

    def get_detail_child_names(self, edge_filter=EdgeFilter()):
        """Yield child names."""
        return ("[%i]" % row for row in range(list.__len__(self)))


class Array(_ListWrap):
    """A general purpose class for 1 or 2 dimensional arrays consisting of
    either BasicBase or StructBase elements."""

    logger = logging.getLogger("pyffi.nif.data.array")
    arg = None  # default argument

    def __init__(
            self,
            name=None,
            element_type=None,
            element_type_template=None,
            element_type_argument: Optional[Expression] = None,
            length=None, width=None,
            parent=None):
        """Initialize the array type.

        :param name: The name of this array, used for error logging and debugging
        :param element_type: The class describing the type of each element.
        :param element_type_template: If the class takes a template type
            argument, then this argument describes the template type.
        :param element_type_argument: If the class takes a type argument, then
            it is described here.
        :param length: An C{Expression} describing the count (first dimension).
        :param width: Either ``None``, or an C{Expression} describing the
            second dimension count.
        :param parent: The parent of this instance, that is, the instance this
            array is an attribute of."""
        if width is None:
            _ListWrap.__init__(self,
                               element_type=element_type, parent=parent)
        else:
            _ListWrap.__init__(self,
                               element_type=_ListWrap, parent=parent)
        self._name = name
        self._parent = weakref.ref(parent) if parent else None
        self._length = length
        self._width = width
        self._elementType = element_type
        self._elementTypeTemplate = element_type_template
        self._elementTypeArgument = element_type_argument

        try:
            if self._width is None:
                for i in range(self._lengthT()):
                    elem_instance = self._elementType(
                        template=self._elementTypeTemplate,
                        argument=self._elementTypeArgument,
                        parent=self)
                    self.append(elem_instance)
            else:
                for i in range(self._lengthT()):
                    elem = _ListWrap(element_type=element_type, parent=self)
                    for j in range(self._widthT(i)):
                        elem_instance = self._elementType(
                            template=self._elementTypeTemplate,
                            argument=self._elementTypeArgument,
                            parent=elem)
                        elem.append(elem_instance)
                    self.append(elem)
        except ArithmeticError:
            self.logger.exception("Failed to initialize default array")

    def _lengthT(self):
        """The _length the array should have, obtained by evaluating the _length expression."""
        if self._parent is None:
            return int(self._length.eval())
        else:
            return int(self._length.eval(self._parent()))

    def _widthT(self, index1):
        """The _length the array should have, obtained by evaluating the width expression."""
        if self._width is None:
            raise ValueError('single array treated as double array (bug?)')
        if self._parent is None:
            expr = self._width.eval()
        else:
            expr = self._width.eval(self._parent())
        if isinstance(expr, int):
            return expr
        elif isinstance(expr, float):
            return int(expr)
        else:
            return int(expr[index1])

    def deepcopy(self, block):
        """Copy attributes from a given array which needs to have at least as many elements (possibly more) as self."""
        if self._width is None:
            for i in range(self._lengthT()):
                attrvalue = self[i]
                if isinstance(attrvalue, StructBase):
                    attrvalue.deepcopy(block[i])
                elif isinstance(attrvalue, Array):
                    attrvalue.update_size()
                    attrvalue.deepcopy(block[i])
                else:
                    self[i] = block[i]
        else:
            for i in range(self._lengthT()):
                for j in range(self._widthT(i)):
                    attrvalue = self[i][j]
                    if isinstance(attrvalue, StructBase):
                        attrvalue.deepcopy(block[i][j])
                    elif isinstance(attrvalue, Array):
                        attrvalue.update_size()
                        attrvalue.deepcopy(block[i][j])
                    else:
                        self[i][j] = block[i][j]

    # string of the array
    def __str__(self):
        text = '%s instance at 0x%08X\n' % (self.__class__, id(self))
        if self._width is None:
            for i, element in enumerate(list.__iter__(self)):
                if i > 16:
                    text += "etc...\n"
                    break
                text += "%i: %s" % (i, element)
                if text[-1:] != "\n":
                    text += "\n"
        else:
            k = 0
            for i, elemlist in enumerate(list.__iter__(self)):
                for j, elem in enumerate(list.__iter__(elemlist)):
                    if k > 16:
                        text += "etc...\n"
                        break
                    text += "%i, %i: %s" % (i, j, elem)
                    if text[-1:] != "\n":
                        text += "\n"
                    k += 1
                if k > 16:
                    break
        return text

    def update_size(self):
        """Update the array size. Call this function whenever the size
        parameters change in C{parent}."""
        ## TODO also update row numbers
        old_size = len(self)
        new_size = self._lengthT()
        if self._width is None:
            if new_size < old_size:
                del self[new_size:old_size]
            else:
                for i in range(new_size - old_size):
                    elem = self._elementType(
                        template=self._elementTypeTemplate,
                        argument=self._elementTypeArgument)
                    self.append(elem)
        else:
            if new_size < old_size:
                del self[new_size:old_size]
            else:
                for i in range(new_size - old_size):
                    self.append(_ListWrap(self._elementType))
            for i, elemlist in enumerate(list.__iter__(self)):
                old_size_i = len(elemlist)
                new_size_i = self._widthT(i)
                if new_size_i < old_size_i:
                    del elemlist[new_size_i:old_size_i]
                else:
                    for j in range(new_size_i - old_size_i):
                        elem = self._elementType(
                            template=self._elementTypeTemplate,
                            argument=self._elementTypeArgument)
                        elemlist.append(elem)

    def read(self, stream, data):
        """Read array from stream."""
        # parse arguments
        if self.arg is not None:
            self._elementTypeArgument = self.arg

        # check array size
        length = self._lengthT()
        self.logger.debug("Reading array of size " + str(length))
        if length > 0x10000000:
            raise ValueError('Array %s too long (%i)' % (self._name, length))
        del self[0:self.__len__()]

        # read array
        if self._width is None:
            for i in range(length):
                element = self._elementType(
                    template=self._elementTypeTemplate,
                    argument=self._elementTypeArgument,
                    parent=self)
                element.read(stream, data)
                self.append(element)
        else:
            for i in range(length):
                width = self._widthT(i)
                if width > 0x10000000:
                    raise ValueError('array too long (%i)' % width)
                element_list = _ListWrap(self._elementType, parent=self)
                for j in range(width):
                    element = self._elementType(
                        template=self._elementTypeTemplate,
                        argument=self._elementTypeArgument,
                        parent=element_list)
                    element.read(stream, data)
                    element_list.append(element)
                self.append(element_list)

    def write(self, stream, data):
        """Write array to stream."""
        self._elementTypeArgument = self.arg
        len1 = self._lengthT()
        if len1 != self.__len__():
            raise ValueError('array size (%i) different from to field describing number of elements (%i)' %
                             (self.__len__(), len1))
        if len1 > 0x10000000:
            raise ValueError('array too long (%i)' % len1)
        if self._width is None:
            for elem in list.__iter__(self):
                elem.write(stream, data)
        else:
            for i, elemlist in enumerate(list.__iter__(self)):
                len2i = self._widthT(i)
                if len2i != elemlist.__len__():
                    raise ValueError("array size (%i) different from to field describing number of elements (%i)" %
                                     (elemlist.__len__(), len2i))
                if len2i > 0x10000000:
                    raise ValueError('array too long (%i)' % len2i)
                for elem in list.__iter__(elemlist):
                    elem.write(stream, data)

    def fix_links(self, data):
        """Fix the links in the array by calling C{fix_links} on all elements
        of the array."""
        if not self._elementType._has_links:
            return
        for elem in self._elementList():
            elem.fix_links(data)

    def get_links(self, data=None):
        """Return all links in the array by calling C{get_links} on all elements
        of the array."""
        links = []
        if not self._elementType._has_links:
            return links
        for elem in self._elementList():
            links.extend(elem.get_links(data))
        return links

    def get_strings(self, data):
        """Return all strings in the array by calling C{get_strings} on all
        elements of the array."""
        strings = []
        if not self._elementType._has_strings:
            return strings
        for elem in self._elementList():
            strings.extend(elem.get_strings(data))
        return strings

    def get_refs(self, data=None):
        """Return all references in the array by calling C{get_refs} on all
        elements of the array."""
        links = []
        if not self._elementType._has_links:
            return links
        for elem in self._elementList():
            links.extend(elem.get_refs(data))
        return links

    def get_size(self, data=None):
        """Calculate the sum of the size of all elements in the array."""
        return sum(
            (elem.get_size(data) for elem in self._elementList()), 0)

    def get_hash(self, data=None):
        """Calculate a hash value for the array, as a tuple."""
        hsh = []
        for elem in self._elementList():
            hsh.append(elem.get_hash(data))
        return tuple(hsh)

    def replace_global_node(self, old_branch, new_branch, **kwargs):
        """Calculate a hash value for the array, as a tuple."""
        for elem in self._elementList():
            elem.replace_global_node(old_branch, new_branch, **kwargs)

    def _elementList(self, **kwargs):
        """Generator for listing all elements."""
        if self._width is None:
            for elem in list.__iter__(self):
                yield elem
        else:
            for elemlist in list.__iter__(self):
                for elem in list.__iter__(elemlist):
                    yield elem


from pyffi.object_models.xml.struct_ import StructBase
