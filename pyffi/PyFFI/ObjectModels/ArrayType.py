"""Defines base class for arrays of data.

>>> from PyFFI.ObjectModels.SimpleType import SimpleType
>>> class Int(SimpleType):
...     def __init__(self, value=0):
...         self._value = int(value)
...     def getValue(self):
...         return self._value
...     def setValue(self, value):
...         self._value = int(value)
...     def __str__(self):
...         return "%i (integer)" % self._value
>>> class IntArray(ArrayType):
...     _elementtype = Int
>>> listofints = IntArray()
>>> listofints.append("eek!") # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
ValueError: ...
>>> listofints.append(3)
>>> listofints[0] = 3
>>> listofints.extend([1,2,3,4])
>>> listofints[-1]
4
>>> len(listofints)
5
"""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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

from types import NoneType
import PyFFI.ObjectModels.AnyType
import PyFFI.ObjectModels.SimpleType
import PyFFI.ObjectModels.Tree

def raiseNotImplementedError(*args, **kwargs):
    """Helper function."""
    raise NotImplementedError

class MetaArrayType(type):
    """Metaclass for ArrayType."""
    def __init__(cls, name, bases, dct):
        # create the class
        super(MetaArrayType, cls).__init__(name, bases, dct)
        # customize it
        if issubclass(cls._elementtype,
                      PyFFI.ObjectModels.SimpleType.SimpleType):
            cls.__iter__ = (lambda self:
                            (item.getValue() for item in list.__iter__(self)))
            cls.__getitem__ = (lambda self, index:
                               list.__getitem__(self, index).getValue())
            cls.__setitem__ = (lambda self, index, value:
                               list.__getitem__(self, index).setValue(value))
            cls.__contains__ = (lambda self, value:
                                list.__contains__(cls._elementtype(value)))
            cls.append = (lambda self, value:
                          list.append(self, cls._elementtype(value)))
            cls.count = (lambda self, value:
                         list.count(self, cls._elementtype(value)))
            cls.extend = (lambda self, valuelist:
                          list.extend(self, (cls._elementtype(value)
                                             for value in valuelist)))
            cls.index = (lambda self, value:
                         list.index(self, cls._elementtype(value)))
            cls.insert = (lambda self, index, value:
                          list.insert(self, index, cls._elementtype(value)))
            cls.pop = (lambda self, *arg:
                       list.pop(self, *arg).getValue())
            cls.remove = (lambda self, value:
                          list.remove(self, cls._elementtype(value)))

        cls.__add__ = raiseNotImplementedError
        cls.__delitem__ = raiseNotImplementedError
        cls.__delslice__ = raiseNotImplementedError
        cls.__gt__ = raiseNotImplementedError
        cls.__iadd__ = raiseNotImplementedError
        cls.__imul__ = raiseNotImplementedError
        cls.__le__ = raiseNotImplementedError
        cls.__lt__ = raiseNotImplementedError
        cls.__mul__ = raiseNotImplementedError
        cls.__reduce__ = raiseNotImplementedError
        cls.__reduce_ex__ = raiseNotImplementedError
        cls.__rmul__ = raiseNotImplementedError
        cls.__setslice__ = raiseNotImplementedError

# derives from DetailTreeBranch because arrays types can be displayed in the
# detail view, as branches of the display tree
class ArrayType(PyFFI.ObjectModels.AnyType.AnyType,
                PyFFI.ObjectModels.Tree.DetailTreeBranch,
                list):
    """Base class from which all array types are derived."""
    __metaclass__ = MetaArrayType
    _elementtype = NoneType

    def __getitem__(self, index):
        """Return item at index.

        @param index: The index of the item to return.
        @type index: int
        """
        listitem = list.__getitem__(self, index)
        if isinstance(listitem, PyFFI.ObjectModels.SimpleType.SimpleType):
            return listitem.getValue()
        else:
            return listitem

    def __setitem__(self, index, value):
        """Set item value at index.

        @param index: The index of the item to set.
        @type index: int
        @param value: The value of the item to set.
        @type value: any (whatever value that is appropriate)
        """
        raise NotImplementedError

    def __iter__(self):
        """Iterate over all elements."""
        raise NotImplementedError

    def __contains__(self, value):
        """Check whether the array contains a particular value."""
        raise NotImplementedError

