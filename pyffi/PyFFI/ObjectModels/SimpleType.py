"""Defines the base class for simple types."""

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
import PyFFI.ObjectModels.Tree

# derives from DetailTreeLeaf because simple types can be displayed in the
# detail view, as leafs of the display tree
class SimpleType(PyFFI.ObjectModels.AnyType.AnyType,
                 PyFFI.ObjectModels.Tree.DetailTreeLeaf):
    """Base class from which all simple types are derived. Simple
    types contain data which is not divided further into smaller pieces,
    and that can represented efficiently by a (usually native) Python type,
    typically C{int}, C{float}, or L{str}.

    When overriding this class, set L{ValueType} to the type used to store
    this data. If it is a native type but requires extra validation
    (for example if not all Python values are admissible), derive a wrapper
    class around the native type and place an extra check in C{__new__}.

    Also override L{read} and L{write} if you wish to read and write data
    of this type, and L{identityGenerator} to implement the L{__eq__} and
    L{__neq__} methods efficiently.

    When instantiating simple types which are part of larger objects such as
    L{ArrayType} or L{StructType}, pass these as L{parent} keyword argument
    to the constructor.

    A brief example of usage:

    >>> class shortint(int):
    ...     def __new__(cls, *args, **kwargs):
    ...         # for the sake of example, default value is 3
    ...         val = int(args[0]) if args else 3
    ...         if val < -0x8000 or val > 0x7fff:
    ...             raise ValueError("value %i out of range" % val)
    ...         return super(shortint, cls).__new__(cls, val)
    >>> class Short(SimpleType):
    ...     ValueType = shortint
    >>> test = Short()
    >>> print(test)
    3
    >>> test.value = test.ValueType(255)
    >>> print(test)
    255
    >>> Short(value=100000) # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...
    >>> print(Short(value=15))
    15

    @warning: When assigning to L{value}, it is good practice always to use
        the L{ValueType} class, as in

            >>> some.value = some.ValueType(somevalue) # doctest: +SKIP

        This ensures that the value you assign is indeed of type
        L{ValueType} and has an admissible value. If this is violated, you may
        encounter hard to debug errors.

    @cvar ValueType: The type used to store the data.
    @type ValueType: C{type}
    @ivar value: The actual data.
    @type value: L{ValueType}
    @ivar parent: The parent of this data in the detail tree view.
    @type parent: L{DetailTreeBranch}
    """
    # using __slots__ saves memory
    __slots__ = ["value", "parent"]
    # value type
    ValueType = NoneType

    def __init__(self, **kwargs):
        """Initialize the type with given value and parent.

        @keyword parent: The L{parent} of the object (default is C{None}).
        @type parent: L{DetailTreeBranch} or C{NoneType}
        @keyword value: The initial value of the object. This value is passed
            as an argument to L{ValueType}.
        @type value: L{ValueType}, or anything acceptable as a first argument
            to the L{ValueType} constructor.
        """
        # set value
        if not "value" in kwargs:
            self.value = self.ValueType()
        else:
            self.value = self.ValueType(kwargs["value"])
        # set parent
        self.parent = kwargs.get("parent")
        if not isinstance(self.parent,
                          (NoneType,
                           PyFFI.ObjectModels.Tree.DetailTreeBranch)):
            raise TypeError(
                "parent argument must be a DetailTreeBranch, not a %s"
                % self.parent.__class__.__name__)

    def __str__(self):
        """String representation. This implementation is simply a wrapper
        around C{self.L{value}.__str__()}.

        @return: String representation.
        @rtype: C{str}
        """
        return self.value.__str__()

    def getDetailTreeParent(self):
        """Returns L{parent}.

        @return: L{parent}.
        @rtype: L{DetailTreeBranch}
        """
        return self.parent

    def getDetailTreeDataDisplay(self):
        """Display string for the detail tree. This implementation is simply
        a wrapper around C{self.L{value}.__str__()}.

        @return: String representation.
        @rtype: C{str}
        """
        return self.value.__str__()

