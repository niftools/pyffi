"""Defines the base class and its corresponding metaclass for simple types."""

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

import PyFFI.ObjectModels.AnyType
import PyFFI.ObjectModels.Tree

class MetaSimpleType(type):
    """Metaclass for L{SimpleType}. Sets the L{ValueType<SimpleType.ValueType>}
    class variable.
    """
    def __init__(cls, name, bases, dct):
        """Set C{cls.L{ValueType<SimpleType.ValueType>}} as
        C{type(cls.L{default<SimpleType.default>})}.
        """
        super(MetaSimpleType, cls).__init__(name, bases, dct)
        cls.ValueType = type(cls.default)

# derives from DetailTreeLeaf because simple types can be displayed in the
# detail view, as leafs of the display tree
class SimpleType(PyFFI.ObjectModels.AnyType.AnyType,
                 PyFFI.ObjectModels.Tree.DetailTreeLeaf):
    """Base class from which all simple types are derived. Simple
    types contain data which is not divided further into smaller pieces,
    and that can represented efficiently by a (usually native) Python type,
    typically C{int}, C{float}, or L{str}.

    When overriding this class, set L{default} to whatever default value for
    this data. The type of L{default} also determines the type used to
    represent this data into Python. If this type requires extra validation
    (for example if not all Python values are admissible), also override
    the class method L{makeValue} with additional checks.

    Also override L{read} and L{write} if you wish to read and write data
    of this type, and L{identityGenerator} to implement the L{__eq__} and
    L{__neq__} methods efficiently.

    When instantiating simple types which are part of larger objects such as
    L{ArrayType} or L{StructType}, pass these as L{parent} keyword argument
    to the constructor.

    A brief example of usage:

        >>> class Short(SimpleType):
        ...     default = 3
        ...     @classmethod
        ...     def makeValue(cls, value):
        ...         # convert
        ...         val = super(cls, cls).makeValue(value)
        ...         # check range
        ...         if val < -0x8000 or val > 0x7fff:
        ...             raise ValueError("value %i out of range" % val)
        ...         return val
        >>> test = Short()
        >>> print(test)
        3
        >>> test.value = Short.makeValue(255)
        >>> print(test)
        255
        >>> Short.makeValue(100000) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: ...

    @warning: When assigning to L{value}, it is good practice always to use
        the L{makeValue} class method, as in

            >>> some.value = SomeType.makeValue(somevalue) # doctest: +SKIP

        The L{makeValue} class method takes
        special precautions that the value you assign is indeed of type
        L{ValueType} and has an admissible value. If this is violated, you may
        encounter hard to debug errors.

    @cvar default: Default value of the data. This value also determines
        the Python type used to store the data, that is, L{ValueType}.
    @type default: L{ValueType}
    @cvar ValueType: The Python type used to store the data
        (no need to declare, automatically generated from L{default}).
    @type ValueType: C{type}
    @ivar value: The actual data.
    @type value: L{ValueType}
    @ivar parent: The parent of this data in the detail tree view.
    @type parent: L{DetailTreeBranch}
    """
    # magic to create ValueType from default
    __metaclass__ = MetaSimpleType
    # using __slots__ saves memory and prevents accidental creation
    # of other attributes
    __slots__ = ["value", "parent"]
    # default value
    default = None

    def __init__(self, **kwargs):
        """Initialize the type with the value C{default}.

        @keyword parent: The L{parent} of the object (default is C{None}).
        @type parent: L{DetailTreeBranch} or C{NoneType}
        @keyword value: The initial value of the object; if omitted then
            L{default} is chosen. If set, L{makeValue} is called to validate
            the value.
        @type value: L{ValueType}
        """
        # set value
        if not "value" in kwargs:
            self.value = self.default
        else:
            self.value = self.makeValue(kwargs["value"])
        # set parent
        self.parent = kwargs.get("parent")
        if not self.parent is None:
            if not isinstance(self.parent,
                              PyFFI.ObjectModels.Tree.DetailTreeBranch):
                raise TypeError(
                    "parent argument must be a DetailTreeBranch, not a %s"
                    % self.parent.__class__.__name__)

    @classmethod
    def makeValue(cls, value):
        """Convert value to L{ValueType} by calling its constructor with the
        value as argument, and set object value. If not all L{ValueType} values
        are admissible, override this class to perform the extra check.

        @param value: Any value.
        @type value: L{ValueType} or convertible to it
        @return: Validated and converted value. 
        @rtype: L{ValueType}
        """
        try:
            return cls.ValueType(value)
        except (ValueError, TypeError):
            raise ValueError("could not convert %s (of type %s) to %s"
                             % (value, value.__class__.__name__,
                                self.ValueType.__name__))

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

