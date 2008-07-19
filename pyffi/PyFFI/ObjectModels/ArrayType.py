"""Defines base class for arrays of data.

>>> from PyFFI.ObjectModels.SimpleType import SimpleType
>>> class Int(SimpleType):
...     default = 0
>>> class IntArray(ArrayType):
...     ElementType = Int
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

from itertools import izip

import PyFFI.ObjectModels.AnyType
import PyFFI.ObjectModels.SimpleType
import PyFFI.ObjectModels.Tree

def _classequality(class1, class2):
    """Helper function.

    >>> class MyInt(int):
    ...     pass
    >>> _classequality(int, MyInt)
    False
    >>> _classequality(MyInt, int)
    False
    >>> _classequality(int, int)
    True
    >>> _classequality(MyInt, MyInt)
    True

    @return: C{True} if class1 and class2 are subclasses of one another, and
        C{False} otherwise.
    @rtype: C{bool}
    """
    return issubclass(class1, class2) and issubclass(class2, class1)

class MetaArrayAnyType(type):
    """Metaclass for C{ArrayAnyType}. Checks that
    L{ElementType<ArrayAnyType.ElementType>} is an
    L{AnyType<PyFFI.ObjectModels.AnyType.AnyType} subclass.
    """
    def __init__(cls, name, bases, dct):
        """Initialize array type."""
        # create the class
        super(MetaArrayAnyType, cls).__init__(name, bases, dct)
        # check type of elements
        if not issubclass(cls.ElementType, PyFFI.ObjectModels.AnyType.AnyType):
            raise TypeError("array ElementType must be an AnyType subclass")

class ArrayAnyType(PyFFI.ObjectModels.AnyType.AnyType, list):
    """Wrapper for list of elements of uniform type. Overrides all list
    methods to ensure that the elements are of type
    L{ElementType<ArrayAnyType.ElementType>}.

    >>> from PyFFI.ObjectModels.SimpleType import SimpleType
    >>> class MyInt(SimpleType):
    ...     default = 0
    >>> class ListOfInts(ArrayAnyType):
    ...     ElementType = int # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: ...
    >>> class ListOfInts(ArrayAnyType):
    ...     ElementType = MyInt
    >>> ListOfInts.ElementType is MyInt
    True
    >>> testlist = ListOfInts()
    >>> print(testlist + [0]) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    TypeError: ...
    >>> print(testlist + [MyInt(value=val) for val in xrange(2, 10, 2)])
    MyInt array:
      [00] 2
      [01] 4
      [02] 6
      [03] 8
    <BLANKLINE>

    @cvar ElementType: Type of the elements of this array.
    @type ElementType: L{PyFFI.ObjectModels.AnyType.AnyType}
    @cvar MAXSTR: Maximum number of elements to write in the L{__str__} method.
    @type MAXSTR: C{int}
    """
    __metaclass__ = MetaArrayAnyType
    ElementType = PyFFI.ObjectModels.AnyType.AnyType
    MAXSTR = 16

    def __init__(self, **kwargs):
        """Initialize empty list."""
        super(ArrayAnyType, self).__init__()

    def identityGenerator(self, **kwargs):
        """Generator for the identity of this array."""
        for item in self:
            for item_id in item.identityGenerator():
                yield item_id

    def __str__(self):
        """String representation.

        @return: String representation.
        @rtype: C{str}
        """
        result = "%s array:\n" % self.ElementType.__name__
        more = False
        for itemnum, item in enumerate(self):
            if itemnum >= self.MAXSTR:
                more = True
                break
            result += "  [%02i] %s\n" % (itemnum, item)
        if more:
            result += ("  ...  (%i more following)\n"
                       % (len(self) - self.MAXSTR))
        return result

    def __add__(self, other):
        """Checks type and appends other list.

        @param other: Another list.
        @type other: C{list}
        """
        # type check
        if isinstance(other, ArrayAnyType):
            # fast: only single type check needed
            if not _classequality(other.ElementType, self.ElementType):
                raise TypeError("array has incompatible element type")
        elif isinstance(other, list):
            # slower: check type of all items
            for item in other:
                if not _classequality(type(item), self.ElementType):
                    raise TypeError("list has incompatible element types")
        else:
            # all other cases: failure
            raise TypeError("cannot add %s to array"
                            % other.__class__.__name__)

        # when subclassing from list, the __add__ function still returns a list
        # and not the subclass, so we must reimplement the function, without
        # the list __add__ function: do extend(self), followed by extend(other)
        result = self.__class__()
        result.extend(self)
        result.extend(other)
        return result

class MetaArrayType(type):
    """Metaclass for C{ArrayType}."""
    def __init__(cls, name, bases, dct):
        """Initialize array type."""
        # TODO: add base class depending on element type
        bases = (ArrayAnyType,) + bases
        # create the class
        super(MetaArrayType, cls).__init__(name, bases, dct)

# derives from DetailTreeBranch because arrays types can be displayed in the
# detail view, as branches of the display tree
class ArrayType(PyFFI.ObjectModels.Tree.DetailTreeBranch):
    """Base class from which all array types are derived."""
    __metaclass__ = MetaArrayType
    ElementType = PyFFI.ObjectModels.SimpleType.SimpleType

    def __init__(self, **kwargs):
         """Initialize empty list. No keyword arguments are passed down the
         class hierarchy.
         """
         super(ArrayType, self).__init__()

