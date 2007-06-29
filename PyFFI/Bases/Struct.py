# --------------------------------------------------------------------------
# PyFFI.Bases.Struct
# Implements class for struct types (xml tags <struct>, <compound>
# and <niblock>).
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
from Array import Array

from types import *
from functools import partial



# TODO find a general purpose mechanism to unify the getRefs getLinks and
# getStrings stuff



# This metaclass checks for the presence of an _attrs and _isTemplate
# attributes. For each attribute in _attrs, an
# <attrname> property is generated which gets and sets basic types,
# and gets other types (struct and array). Used as metaclass of
# StructBase.
class _MetaStructBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('_attrs'):
            raise TypeError(str(cls) + ': missing _attrs attribute')
        if not dct.has_key('_isTemplate'):
            raise TypeError(str(cls) + ': missing _isTemplate attribute')
        # hasLinks, hasRefs, hasStrings, used for optimization of fixLinks, getLinks, getRefs, and getStrings
        cls._hasLinks = getattr(cls, '_hasLinks', False) # does the type contain a Ref or a Ptr?
        cls._hasRefs = getattr(cls, '_hasRefs', False) # does the type contain a Ref?
        cls._hasStrings = getattr(cls, '_hasStrings', False) # does the type contain a strng?
        for attrname, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in dct['_attrs']:
            if issubclass(typ, BasicBase) and arr1 == None:
                # get and set basic attributes
                setattr(cls, attrname, property(
                    partial(StructBase.getBasicAttribute, name = attrname),
                    partial(StructBase.setBasicAttribute, name = attrname),
                    doc=doc))
            elif typ == NoneType and arr1 == None:
                # get and set template attributes
                setattr(cls, attrname, property(
                    partial(StructBase.getTemplateAttribute, name = attrname),
                    partial(StructBase.setTemplateAttribute, name = attrname),
                    doc=doc))
            else:
                # other types of attributes: get only
                setattr(cls, attrname, property(
                    partial(StructBase.getAttribute, name = attrname),
                    doc=doc))
            # check for links and refs and strings
            if not cls._hasLinks:
                if typ != type(None): # templates!
                    if typ._hasLinks:
                        cls._hasLinks = True
                #else:
                #    cls._hasLinks = True # or false... we can't know at this point? might be necessary to uncomment this if template types contain refs

            if not cls._hasRefs:
                if typ != type(None):
                    if typ._hasRefs:
                        cls._hasRefs = True
                #else:
                #    cls._hasRefs = True # dito, see comment above

            if not cls._hasStrings:
                if typ != type(None):
                    if typ._hasStrings:
                        cls._hasStrings = True
                #else:
                #    cls._hasRefs = True # dito, see comment above
        # precalculate the attribute list
        cls._attributeList = cls._getAttributeList()

class StructBase(object):
    """Base class from which all file struct types are derived.

    The StructBase class implements the basic struct interface:
    it will initialize all attributes using the class interface
    using the _attrs class variable, print them as strings, and so on.
    The class variable _attrs must be declared every derived class
    interface.

    Each item in the class _attrs list stores the information about
    the attribute as stored for instance in the xml file, and the
    _<name>_value_ instance variable stores the actual attribute
    instance.

    Direct access to the attributes is implemented using a <name>
    property which invokes the getAttribute and setAttribute
    functions, as demonstrated below.

    See the PyFFI.XmlHandler class for a more advanced example.

    >>> from Basic import BasicBase
    >>> class UInt(BasicBase):
    ...     _isTemplate = False
    ...     def __init__(self, template = None, argument = None):
    ...         self.__value = 0
    ...     def getValue(self):
    ...         return self.__value
    ...     def setValue(self, value):
    ...         self.__value = int(value)
    >>> class X(StructBase):
    ...     _isTemplate = False
    ...     _attrs = [
    ...         ('a', UInt, None, None, None, None, None, None, None, None, None, None),
    ...         ('b', UInt, None, None, None, None, None, None, None, None, None, None)]
    >>> class Y(X):
    ...     _isTemplate = False
    ...     _attrs = [
    ...         ('c', UInt, None, None, None, None, None, None, None, None, None, None),
    ...         ('d', X, None, None, None, None, None, Expression('c == 3'), None, None, None, None)]
    >>> y = Y()
    >>> y.a = 1
    >>> y.b = 2
    >>> y.c = 3
    >>> y.d.a = 4
    >>> y.d.b = 5
    >>> print y # doctest:+ELLIPSIS
    <class 'PyFFI.Bases.Struct.Y'> instance at 0x...
    * a : 1
    * b : 2
    * c : 3
    * d :
        <class 'PyFFI.Bases.Struct.X'> instance at 0x...
        * a : 4
        * b : 5
    <BLANKLINE>
    >>> y.d = 1
    Traceback (most recent call last):
        ...
    AttributeError: can't set attribute
    """
    
    __metaclass__ = _MetaStructBase
    
    _isTemplate = False
    _attrs = []
    
    # initialize all attributes
    def __init__(self, template = None, argument = None):
        """The constructor takes a tempate: any attribute whose type,
        or template type, is type(None) - which corresponds to
        TEMPLATE in the xml description - will be replaced by this
        type. The argument is what the ARG xml tags will be replaced with."""
        # used to track names of attributes that have already been added
        # is faster than self.__dict__.has_key(...)
        names = []
        # initialize argument
        self.arg = argument
        # initialize attributes
        for name, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in self._attributeList:
            # skip dupiclate names
            # (for this to work properly, duplicate names must have the same
            # typ, tmpl, arg, arr1, and arr2)
            if name in names: continue
            names.append(name)
            # handle template
            if typ == type(None):
                #assert(template != type(None))
                #assert(self._isTemplate)
                typ = template
            if tmpl == type(None):
                #assert(template != type(None))
                #assert(self._isTemplate)
                tmpl = template
            # handle argument
            if arg != None:
                if not isinstance(arg, (int, long)):
                    arg = getattr(self, arg)
            # handle arrays
            if arr1 == None:
                attr_instance = typ(tmpl, arg)
                if default != None:
                    attr_instance.setValue(default)
            elif arr2 == None:
                attr_instance = Array(self, typ, tmpl, arg, arr1)
            else:
                attr_instance = Array(self, typ, tmpl, arg, arr1, arr2)
            # assign attribute value
            setattr(self, "_" + name + "_value_", attr_instance)

    # string of all attributes
    def __str__(self):
        s = '%s instance at 0x%08X\n'%(self.__class__, id(self))
        # used to track names of attributes that have already been added
        # is faster than self.__dict__.has_key(...)
        names = []
        for name, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in self._attributeList:
            # skip dupiclate names
            if name in names: continue
            names.append(name)
            if cond != None:
                if not cond.eval(self): continue
            attr_str_lines = str(getattr(self, "_" + name + "_value_")).splitlines()
            if len(attr_str_lines) > 1:
                s += '* ' + str(name) + ' :\n'
                for attr_str in attr_str_lines:
                    s += '    ' + attr_str + '\n'
            else:
                s += '* ' + str(name) + ' : ' + attr_str_lines[0] + '\n'
        return s

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], string_list = [], argument = None):
        self.arg = argument
        for name, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in self._attributeList:
            if ver1:
                if version < ver1: continue
            if ver2:
                if version > ver2: continue
            if userver:
                if user_version != userver: continue
            if cond != None:
                if not cond.eval(self): continue
            if arg != None:
                if not isinstance(arg, (int, long)):
                    arg = getattr(self, arg)
            getattr(self, "_" + name + "_value_").read(version, user_version, f, link_stack, string_list, arg)

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, string_list = [], argument = None):
        self.arg = argument
        for name, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in self._attributeList:
            if ver1:
                if version < ver1: continue
            if ver2:
                if version > ver2: continue
            if userver:
                if user_version != userver: continue
            if cond != None:
                if not cond.eval(self): continue
            if arg != None:
                if not isinstance(arg, (int, long)):
                    arg = getattr(self, arg)
            getattr(self, "_" + name + "_value_").write(version, user_version, f, block_index_dct, string_list, arg)

    def fixLinks(self, version, user_version, block_dct, link_stack):
        for name, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in self._attributeList:
            if not typ._hasLinks: continue
            if ver1:
                if version < ver1: continue
            if ver2:
                if version > ver2: continue
            if userver:
                if user_version != userver: continue
            if cond != None:
                if not cond.eval(self): continue
            getattr(self, "_" + name + "_value_").fixLinks(version, user_version, block_dct, link_stack)

    def getLinks(self, version, user_version):
        links = []
        for name, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in self._attributeList:
            if not typ._hasLinks: continue
            if ver1:
                if version < ver1: continue
            if ver2:
                if version > ver2: continue
            if userver:
                if user_version != userver: continue
            if cond != None:
                if not cond.eval(self): continue
            links.extend(getattr(self, "_" + name + "_value_").getLinks(version, user_version))
        return links

    def getStrings(self, version, user_version):
        strings = []
        for name, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in self._attributeList:
            if not typ._hasStrings: continue
            if ver1:
                if version < ver1: continue
            if ver2:
                if version > ver2: continue
            if userver:
                if user_version != userver: continue
            if cond != None:
                if not cond.eval(self): continue
            strings.extend(getattr(self, "_" + name + "_value_").getStrings())
        return strings

    def getRefs(self):
        links = []
        for name, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver, doc in self._attributeList:
            if not typ._hasLinks: continue
            links.extend(getattr(self, "_" + name + "_value_").getRefs())
        return links

    @classmethod
    def _getAttributeList(cls):
        # string of attributes of base classes of cls
        attrs = []
        for base in cls.__bases__:
            try:
                attrs.extend(base._getAttributeList())
            except AttributeError:
                pass
        attrs.extend(cls._attrs)
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

    def getTemplateAttribute(self, name):
        """Get a template attribute."""
        try:
            return self.getBasicAttribute(name)
        except AttributeError:
            return self.getAttribute(name)

    # important note: to apply partial(setAttribute, name = 'xyz') the
    # name argument must be last
    def setTemplateAttribute(self, value, name):
        """Set the value of a template attribute."""
        try:
            self.setBasicAttribute(value, name)
        except AttributeError:
            raise NotImplementedError("cannot set '%s' attribute"%name)
