# --------------------------------------------------------------------------
# FileFormat.Bases.Compound
# Implements class for compound types (xml tags <compound> and <niblock>).
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
from Expression import Expression
from Array import Array

try:
    from functools import partial
except ImportError: # quick hack for python < 2.5
    class partial(object):
        def __init__(self, fn, name):
            self.fn = fn
            self.name = name
        def __call__(self, *args):
            return self.fn(*args, **{ 'name' : self.name } )

# This metaclass checks for the presence of an _attrs, _isTemplate,
# and _isAbstract attribute. For each <attrname> in _attrs, it also
# checks for _info_<attrname>_ class attributes, and generates an
# <attrname> property which gets and sets basic types, and gets other
# types (compound and array). Used as metaclass of CompoundBase.
class _MetaCompoundBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('_attrs'):
            raise TypeError(str(cls) + ': missing _attrs attribute')
        if not dct.has_key('_isTemplate'):
            raise TypeError(str(cls) + ': missing _isTemplate attribute')
        if not dct.has_key('_isAbstract'):
            raise TypeError(str(cls) + ': missing _isAbstract attribute')
        for attrname in dct['_attrs']:
            if not dct.has_key('_' + attrname + '_info_'):
                raise TypeError(str(cls) + ': missing _' + attrname + '_info_ attribute')
            if issubclass(dct['_' + attrname + '_info_'][0], BasicBase):
                # get and set basic attributes
                setattr(cls, attrname, property(
                    partial(CompoundBase.getBasicAttribute, name = attrname),
                    partial(CompoundBase.setBasicAttribute, name = attrname)))
            else:
                # other types of attributes: get only
                setattr(cls, attrname, property(
                    partial(CompoundBase.getAttribute, name = attrname)))

class CompoundBase(object):
    """Base class from which all file compound types are derived.

    The CompoundBase class implements the basic compound interface:
    it will initialize all attributes using the class interface
    using the _attrs class variable, print them as strings, and so on.
    The class variable _attrs must be declared every derived class
    interface.

    For each string <name> in the _attrs list, there must be a class
    variable _<name>_info_. Upon instanciation, the compound will create an
    instance variable _<name>_value_. The _<name>_info_ class variable
    stores the information about the attribute as stored for instance
    in the xml file, and the _<name>_value_ instance variable stores the
    actual attribute instance.

    Direct access to the attributes is implemented using a <name>
    property which invokes the getAttribute and setAttribute
    functions, as demonstrated below.

    See the FileFormat.XmlHandler class for a more advanced example.

    >>> from Basic import BasicBase
    >>> class UInt(BasicBase):
    ...     _isTemplate = False
    ...     def __init__(self):
    ...         self.__value = 0
    ...     def getValue(self):
    ...         return self.__value
    ...     def setValue(self, value):
    ...         self.__value = int(value)
    >>> class X(CompoundBase):
    ...     _isTemplate = False
    ...     _isAbstract = True
    ...     _attrs = ['a', 'b']
    ...     _a_info_ = (UInt, None, None, None, None, None, None, None, None, None)
    ...     _b_info_ = (UInt, None, None, None, None, None, None, None, None, None)
    >>> class Y(X):
    ...     _isTemplate = False
    ...     _isAbstract = True
    ...     _attrs = ['c', 'd']
    ...     _c_info_ = (UInt, None, None, None, None, None, None, None, None, None)
    ...     _d_info_ = (X, None, None, None, None, None, None, None, None, None)
    >>> y = Y()
    >>> print y.getAttributeNames()
    ['a', 'b', 'c', 'd']
    >>> y.a = 1
    >>> y.b = 2
    >>> y.c = 3
    >>> y.d.a = 4
    >>> y.d.b = 5
    >>> print y # doctest:+ELLIPSIS
    <class 'FileFormat.Bases.Compound.Y'> instance at 0x...
    * a : 1
    * b : 2
    * c : 3
    * d :
        <class 'FileFormat.Bases.Compound.X'> instance at 0x...
        * a : 4
        * b : 5
    <BLANKLINE>
    >>> y.d = 1
    Traceback (most recent call last):
        ...
    AttributeError: can't set attribute
    """
    
    __metaclass__ = _MetaCompoundBase
    
    _isTemplate = False
    _isAbstract = True
    _attrs = []
    
    # initialize all attributes
    def __init__(self, template = type(None)):
        for name in self.getAttributeNames():
            typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver = getattr(self, "_" + name + "_info_")
            if typ == type(None):
                assert(template != type(None))
                assert(self._isTemplate)
                typ = template
            typ_args = []
            if tmpl != None:
                typ_args.append(tmpl)
            #if default:
            #    typ_args.append(default)
            if not isinstance(arr1, Expression):
                attr_instance = typ(*typ_args)
            elif not isinstance(arr2, Expression):
                arr1.setData(self)
                attr_instance = Array(typ, tmpl, arr1) # TODO use Array class
            else:
                attr_instance = [[]] # TODO use Array class
            setattr(self, "_" + name + "_value_", attr_instance)

    # string of all attributes
    def __str__(self):
        s = '%s instance at 0x%08X\n'%(self.__class__, id(self))
        for name in self.getAttributeNames():
            typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver = getattr(self, "_" + name + "_info_")
            attr_str_lines = str(getattr(self, "_" + name + "_value_")).splitlines()
            if len(attr_str_lines) > 1:
                s += '* ' + str(name) + ' :\n'
                for attr_str in attr_str_lines:
                    s += '    ' + attr_str + '\n'
            else:
                s += '* ' + str(name) + ' : ' + attr_str_lines[0] + '\n'
        return s

    @classmethod
    def getAttributeNames(cls):
        # string of attributes of base classes of cls
        attrs = []
        for base in cls.__bases__:
            if issubclass(base, CompoundBase):
                attrs.extend(base.getAttributeNames())
        for name in cls._attrs:
            attrs.append(name)
        return attrs

    def getAttribute(self, name):
        """Get a (non-basic) attribute."""
        return getattr(self, "_" + name + "_value_")

    def getBasicAttribute(self, name):
        """Get a basic attribute."""
        return getattr(self, "_" + name + "_value_").getValue()

    # important note: to apply partial(setAttribute, name = 'xyz') the
    # name argument must be last
    def setBasicAttribute(self, value, name):
        """Set the value of a basic attribute."""
        getattr(self, "_" + name + "_value_").setValue(value)
