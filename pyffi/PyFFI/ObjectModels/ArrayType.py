"""Defines base class for arrays of data.

>>> from PyFFI.ObjectModels.SimpleType import SimpleType
>>> class Int(SimpleType):
...     _ValueType = int
>>> class IntArray(ArrayType):
...     _ElementType = Int
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
    L{_ElementType<ArrayAnyType._ElementType>} is an
    L{AnyType<PyFFI.ObjectModels.AnyType.AnyType>} subclass.
    """
    def __init__(cls, name, bases, dct):
        """Initialize array type."""
        # create the class
        super(MetaArrayAnyType, cls).__init__(name, bases, dct)
        # check type of elements
        if not issubclass(cls._ElementType, PyFFI.ObjectModels.AnyType.AnyType):
            raise TypeError("array _ElementType must be an AnyType subclass")

class ArrayAnyType(PyFFI.ObjectModels.AnyType.AnyType):
    """Wrapper for list of elements of uniform type. Has all of list's
    methods to ensure that the elements are of type
    L{_ElementType<ArrayAnyType._ElementType>}, and that their parent is set.

    >>> from PyFFI.ObjectModels.SimpleType import SimpleType
    >>> class MyInt(SimpleType):
    ...     _ValueType = int
    >>> class ListOfInts(ArrayAnyType):
    ...     _ElementType = MyInt
    >>> testlist = ListOfInts()
    >>> testlist.append(MyInt(value=20))
    >>> testlist.extend([MyInt(value=val) for val in xrange(2, 10, 2)])
    >>> print(testlist)
    MyInt array:
      [00] 20
      [01] 2
      [02] 4
      [03] 6
      [04] 8
    <BLANKLINE>
    >>> [item._value for item in testlist[::-2]]
    [8, 4, 20]

    @cvar _ElementType: Type of the elements of this array.
    @type _ElementType: L{PyFFI.ObjectModels.AnyType.AnyType}
    @cvar _MAXSTR: Maximum number of elements to write in the L{__str__} method.
    @type _MAXSTR: C{int}
    """
    __metaclass__ = MetaArrayAnyType
    _ElementType = PyFFI.ObjectModels.AnyType.AnyType
    _MAXSTR = 16

    def __init__(self, **kwargs):
        """Initialize empty list."""
        super(ArrayAnyType, self).__init__(**kwargs)
        self._items = []

    def identityGenerator(self, **kwargs):
        """Generator for the identity of this array."""
        # compare length
        yield len(self._items)
        # compare elements
        for item in self._items:
            for item_id in item.identityGenerator():
                yield item_id

    def __str__(self):
        """String representation.

        @return: String representation.
        @rtype: C{str}
        """
        result = "%s array:\n" % self._ElementType.__name__
        more = False
        for itemnum, item in enumerate(self._items):
            if itemnum >= self._MAXSTR:
                more = True
                break
            result += "  [%02i] %s\n" % (itemnum, item)
        if more:
            result += ("  ...  (%i more following)\n"
                       % (len(self._items) - self._MAXSTR))
        return result

    def _setItemTreeParent(self, item):
        """Check if item can be added, and sets tree parent (for internal use
        only, this is called on items before they are added to the array).

        @param item: The item to be checked.
        @type item: L{_ElementType}
        @raise C{TypeError}: If item has incompatible type.
        @raise C{ValueError}: If item already has a tree parent.
        """
        # check item
        if not _classequality(type(item), self._ElementType):
            raise TypeError("item has incompatible type (%s, not %s)"
                            % (item.__class__.__name__,
                               self._ElementType.__name__))
        # set item parent
        if item._treeparent is None:
            item._treeparent = self
        else:
            raise ValueError("item already has a tree parent") 

    def __getitem__(self, index):
        """Return item at given index.

        @param index: The index.
        @type index: C{int} or C{slice}
        @return: Item at given index, or slice.
        @rtype: L{_ElementType}, or C{list} of L{_ElementType}
        """
        return self._items[index]

    def __setitem__(self, index, item):
        """Set item at given index. Parent of item currently at index has its
        tree parent removed.

        @param index: The index.
        @type index: C{int}
        @param item: Item to set.
        @type item: L{_ElementType}
        """
        # clear parent of previous item
        self._items[index]._treeparent = None
        # set the new item
        self._setItemTreeParent(item)
        self._items[index] = item

    def __delitem__(self, index):
        """Remove tree parents of item(s) at index or slice, and
        remove the items from the array.

        @param index: The index or slice of items to remove.
        @type index: C{int} or C{slice}
        """
        if isinstance(index, slice):
            for i in xrange(*slice.indices(len(self._items))):
                self._items[i]._treeparent = None
        else:
            self._items[index]._treeparent = None
        self._items.__del__(index)

    def __iter__(self):
        return self._items.__iter__()

    def append(self, item):
        """Set item tree parent and append to array.

        @param item: The item to append.
        @type item: L{_ElementType}
        """
        self._setItemTreeParent(item)
        self._items.append(item)

    def count(self, item):
        return self._items.count(item)

    def extend(self, other):
        """Set tree parent of all items, and extend array.

        @param other: The list to extend with.
        @type other: C{list} of L{_ElementType}
        @raise C{TypeError}: If the types of the list items do not match.
        @raise C{ValueError}: If items already have a tree parent.
        """
        # check type of other
        if not isinstance(other, list):
            raise TypeError("first argument must be list")
        # set tree parents and check type
        for item in other:
            self._setItemTreeParent(item)
        # extend
        self._items.extend(other)

    def index(self, item):
        return self._items.index(item)

    def insert(self, index, item):
        self._setItemTreeParent(item)
        self._items.insert(index, item)

    def pop(self, index=-1):
        self._items[index]._treeparent = None
        return self._items.pop(index)

    def remove(self, item):
        index = self.index(item)
        self._items[index]._treeparent = None
        self.__delitem__(index)

    def reverse(self):
        self._items.reverse()

    def sort(self, cmp=None, key=None, reverse=False):
        self._items.sort(cmp, key, reverse)

class MetaArrayType(type):
    """Metaclass for C{ArrayType}."""
    def __init__(cls, name, bases, dct):
        """Initialize array type."""
        # TODO: add base class depending on element type
        bases = (ArrayAnyType,) + bases
        # create the class
        super(MetaArrayType, cls).__init__(name, bases, dct)

# derives from DetailNode because arrays types can be displayed in the
# detail view, as branches of the display tree
class ArrayType(PyFFI.ObjectModels.Tree.DetailNode):
    """Base class from which all array types are derived.

    @todo: Finish this class.
    """
    __metaclass__ = MetaArrayType
    _ElementType = PyFFI.ObjectModels.SimpleType.SimpleType

    def __init__(self, **kwargs):
         """Initialize empty list. For now, no keyword arguments are passed
         down the class hierarchy.
         """
         super(ArrayType, self).__init__()

