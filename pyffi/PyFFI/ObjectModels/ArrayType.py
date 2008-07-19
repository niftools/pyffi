"""Defines base class for arrays of data.

>>> from PyFFI.ObjectModels.SimpleType import SimpleType
>>> class Int(SimpleType):
...     default = 0
...     def __str__(self):
...         return "%i (integer)" % self.value
...     def identityGenerator(self):
...         yield self.value
>>> class IntArray(ArrayType):
...     ElementType = Int
>>> listofints = IntArray()
>>> listofints.append(IntArray.makeValue("eek!")) # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
ValueError: ...
>>> listofints.append(IntArray.makeValue(3))
>>> listofints[0] = 3
>>> listofints.extend(IntArray.makeArray([1, 2, 3, 4, 9, 10]))
>>> listofints[-1]
10
>>> len(listofints)
7
>>> print(listofints)
>>> for value in listofints:
...     print value
3
1
2
3
4
9
10
>>> 7 in listofints
False
>>> 3 in listofints
True
>>> listofints.index(9)
5
>>> listofints.remove(2)
>>> print(listofints)
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
        """Initialize array type."""
        # create the class
        super(MetaArrayType, cls).__init__(name, bases, dct)
        # customize it
        cls.ElementType = type(cls.default)

# derives from DetailTreeBranch because arrays types can be displayed in the
# detail view, as branches of the display tree
class ArrayType(PyFFI.ObjectModels.AnyType.AnyType,
                PyFFI.ObjectModels.Tree.DetailTreeBranch,
                list):
    """Base class from which all array types are derived."""
    __metaclass__ = MetaArrayType
    default = PyFFI.ObjectModels.SimpleType.SimpleType()

    @classmethod
    def makeValue(cls, value):
        """Wrapper for L{ElementType}.makeValue(value).
        """
        return cls.ElementType.makeValue(value)

    def makeArray(cls, iterable):
        """Returns generator which yields L{ElementType}.makeValue(value) for
        every value in iterable.
        """
        return (cls.ElementType.makeValue(value) for value in iterable)

