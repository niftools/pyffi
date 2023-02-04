"""
:mod:`pyffi.object_models.xml.struct_` --- Structured Types
===================================================================

Implements base class for struct types.

Implementation
--------------

.. autoclass:: StructBase
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: _MetaStructBase
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
from functools import partial
from typing import Optional

import pyffi.object_models.common
from pyffi.object_models.basic import BasicBase
from pyffi.object_models.expression import Expression
from pyffi.utils.graph import GlobalNode, EdgeFilter


class _MetaStructBase(type):
    """This metaclass checks for the presence of _attrs and _is_template
    attributes. For each attribute in _attrs, an
    <attrname> property is generated which gets and sets basic types,
    and gets other types (struct and array). Used as metaclass of
    StructBase."""

    def __init__(cls, name, bases, dct):
        super(_MetaStructBase, cls).__init__(name, bases, dct)
        # does the type contain a Ref or a Ptr?
        cls._has_links = getattr(cls, '_has_links', False)
        # does the type contain a Ref?
        cls._has_refs = getattr(cls, '_has_refs', False)
        # does the type contain a string?
        cls._has_strings = getattr(cls, '_has_strings', False)

        for attr in dct.get('_attrs', []):
            # basestring is a forward compound type declaration
            # and issubclass must take a type as first argument
            # hence this hack
            if not isinstance(attr.type_, str) and \
                    issubclass(attr.type_, BasicBase) and attr.length is None:
                # get and set basic attributes
                setattr(cls, attr.name, property(
                    partial(StructBase.get_basic_attribute, name=attr.name),
                    partial(StructBase.set_basic_attribute, name=attr.name),
                    doc=attr.doc))
            elif not isinstance(attr.type_, str) and \
                    issubclass(attr.type_, StructBase) and attr.length is None:
                # get and set struct attributes
                setattr(cls, attr.name, property(
                    partial(StructBase.get_attribute, name=attr.name),
                    partial(StructBase.set_attribute, name=attr.name),
                    doc=attr.doc))
            elif attr.type_ == type(None) and attr.length is None:
                # get and set template attributes
                setattr(cls, attr.name, property(
                    partial(StructBase.get_template_attribute, name=attr.name),
                    partial(StructBase.set_template_attribute, name=attr.name),
                    doc=attr.doc))
            else:
                # other types of attributes: get only
                setattr(cls, attr.name, property(
                    partial(StructBase.get_attribute, name=attr.name),
                    doc=attr.doc))

            # check for links and refs and strings
            if not cls._has_links:
                if attr.type_ != type(None):  # templates!
                    # attr.type_ basestring means forward declaration
                    # we cannot know if it has links, so assume yes
                    if (isinstance(attr.type_, str)
                            or attr.type_._has_links):
                        cls._has_links = True
                # else:
                #    cls._has_links = True
                # or false... we can't know at this point... might be necessary
                # to uncomment this if template types contain refs

            if not cls._has_refs:
                if attr.type_ != type(None):
                    # attr.type_ basestring means forward declaration
                    # we cannot know if it has refs, so assume yes
                    if (isinstance(attr.type_, str)
                            or attr.type_._has_refs):
                        cls._has_refs = True
                # else:
                #    cls._has_refs = True # dito, see comment above

            if not cls._has_strings:
                if attr.type_ != type(None):
                    # attr.type_ basestring means forward declaration
                    # we cannot know if it has strings, so assume yes
                    if (isinstance(attr.type_, str)
                            or attr.type_._has_strings):
                        cls._has_strings = True
                else:
                    # enabled because there is a template key type that has
                    # strings
                    cls._has_strings = True

        # precalculate the attribute list
        # profiling shows that this speeds up most of the StructBase methods
        # that rely on parsing the attribute list
        cls._attribute_list = cls._get_attribute_list()

        # precalculate the attribute name list
        cls._names = cls._get_names()

    def __repr__(cls):
        return "<struct '%s'>" % cls.__name__


class StructBase(GlobalNode, metaclass=_MetaStructBase):
    """Base class from which all file struct types are derived.

    The StructBase class implements the basic struct interface:
    it will initialize all attributes using the class interface
    using the _attrs class variable, represent them as strings, and so on.
    The class variable _attrs must be declared every derived class
    interface.

    Each item in the class _attrs list stores the information about
    the attribute as stored for instance in the xml file, and the
    _<name>_value_ instance variable stores the actual attribute
    instance.

    Direct access to the attributes is implemented using a <name>
    property which invokes the get_attribute and set_attribute
    functions, as demonstrated below.

    See the pyffi.XmlHandler class for a more advanced example.

    >>> from pyffi.object_models.basic import BasicBase
    >>> from pyffi.object_models.expression import Expression
    >>> from pyffi.object_models.xml import StructAttribute as Attr
    >>> class SimpleFormat(object):
    ...     class UInt(BasicBase):
    ...         _is_template = False
    ...         def __init__(self, **kwargs):
    ...             BasicBase.__init__(self, **kwargs)
    ...             self.__value = 0
    ...         def get_value(self):
    ...             return self.__value
    ...         def set_value(self, value):
    ...             self.__value = int(value)
    ...     @staticmethod
    ...     def name_attribute(name):
    ...         return name
    >>> class X(StructBase):
    ...     _is_template = False
    ...     _attrs = [
    ...         Attr(SimpleFormat, dict(name = 'a', type = 'UInt')),
    ...         Attr(SimpleFormat, dict(name = 'b', type = 'UInt'))]
    >>> SimpleFormat.X = X
    >>> class Y(X):
    ...     _is_template = False
    ...     _attrs = [
    ...         Attr(SimpleFormat, dict(name = 'c', type = 'UInt')),
    ...         Attr(SimpleFormat, dict(name = 'd', type = 'X', cond = 'c == 3'))]
    >>> SimpleFormat.Y = Y
    >>> y = Y()
    >>> y.a = 1
    >>> y.b = 2
    >>> y.c = 3
    >>> y.d.a = 4
    >>> y.d.b = 5
    >>> print(y) # doctest:+ELLIPSIS
    <class 'pyffi.object_models.xml.struct_.Y'> instance at 0x...
    * a : 1
    * b : 2
    * c : 3
    * d :
        <class 'pyffi.object_models.xml.struct_.X'> instance at 0x...
        * a : 4
        * b : 5
    <BLANKLINE>
    >>> y.d = 1
    Traceback (most recent call last):
        ...
    TypeError: expected X but got int
    >>> x = X()
    >>> x.a = 8
    >>> x.b = 9
    >>> y.d = x
    >>> print(y) # doctest:+ELLIPSIS
    <class 'pyffi.object_models.xml.struct_.Y'> instance at 0x...
    * a : 1
    * b : 2
    * c : 3
    * d :
        <class 'pyffi.object_models.xml.struct_.X'> instance at 0x...
        * a : 8
        * b : 9
    <BLANKLINE>

    Attributes:
        _attrs (list[pyffi.object_models.niftoolsxml.StructAttribute]): TODO
    """

    _is_template = False
    _attrs = []
    _games = {}
    arg = None
    logger = logging.getLogger("pyffi.nif.data.struct")

    # initialize all attributes
    def __init__(self, template=None, argument: Optional[Expression] = None, parent=None):
        """The constructor takes a tempate: any attribute whose type,
        or template type, is type(None) - which corresponds to
        TEMPLATE in the xml description - will be replaced by this
        type. The argument is what the ARG xml tags will be replaced with.

        :param template: If the class takes a template type
            argument, then this argument describes the template type.
        :param argument: If the class takes a type argument, then
            it is described here.
        :param parent: The parent of this instance, that is, the instance this
            array is an attribute of."""
        # used to track names of attributes that have already been added
        # is faster than self.__dict__.has_key(...)
        names = set()
        # initialize argument
        self.arg = argument
        # save parent (note: disabled for performance)
        # self._parent = weakref.ref(parent) if parent else None
        # initialize item list
        # this list is used for instance by qskope to display the structure
        # in a tree view
        self._items = []
        self._template = template

        # initialize attributes
        for attr in self._attribute_list:  # Attributes get replaced on read
            # skip attributes with duplicate names
            # (for this to work properly, duplicates must have the same
            # type, template, argument, length, and width)
            if attr.name in names:
                continue
            names.add(attr.name)

            # things that can only be determined at runtime (rt_xxx)
            rt_type = attr.type_ if attr.type_ != type(None) \
                else template
            rt_template = attr.template if attr.template != type(None) \
                else template
            rt_arg = attr.arg.eval(self) if attr.arg is not None else None

            # instantiate the class, handling arrays at the same time
            if attr.length is None:
                attr_instance = rt_type(
                    template=rt_template, argument=rt_arg,
                    parent=self)
                if attr.default is not None:
                    attr_instance.set_value(attr.default)
            elif attr.width is None:
                attr_instance = Array(
                    name=attr.name,
                    element_type=rt_type,
                    element_type_template=rt_template,
                    element_type_argument=rt_arg,
                    length=attr.length,
                    parent=self)
            else:
                attr_instance = Array(
                    name=attr.name,
                    element_type=rt_type,
                    element_type_template=rt_template,
                    element_type_argument=rt_arg,
                    length=attr.length, width=attr.width,
                    parent=self)

            # assign attribute value
            setattr(self, "_%s_value_" % attr.name, attr_instance)

            # add instance to item list
            self._items.append(attr_instance)

    def deepcopy(self, block):
        """Copy attributes from a given block (one block class must be a
        subclass of the other). Returns self."""
        # check class lineage
        if isinstance(self, block.__class__):
            attrlist = block._get_filtered_attribute_list()
        elif isinstance(block, self.__class__):
            attrlist = self._get_filtered_attribute_list()
        else:
            raise ValueError("deepcopy: classes %s and %s unrelated"
                             % (self.__class__.__name__, block.__class__.__name__))
        # copy the attributes
        for attr in attrlist:
            try:
                attrvalue = getattr(self, attr.name)
                if isinstance(attrvalue, (StructBase, BitStructBase)):
                    attrvalue.deepcopy(getattr(block, attr.name))
                elif isinstance(attrvalue, Array):
                    attrvalue.update_size()
                    attrvalue.deepcopy(getattr(block, attr.name))
                else:
                    setattr(self, attr.name, getattr(block, attr.name))
            except Exception:
                self.logger.error("Failed to set attribute %s in block %s", attr.name, block)
                raise

        return self

    # string of all attributes
    def __str__(self):
        text = '%s instance at 0x%08X\n' % (self.__class__, id(self))
        # used to track names of attributes that have already been added
        # is faster than self.__dict__.has_key(...)
        for attr in self._get_filtered_attribute_list():
            # append string
            attr_str_lines = str(
                getattr(self, "_%s_value_" % attr.name, None)).splitlines()
            if len(attr_str_lines) > 1:
                text += '* %s :\n' % attr.name
                for attr_str in attr_str_lines:
                    text += '    %s\n' % attr_str
            elif attr_str_lines:
                text += '* %s : %s\n' % (attr.name, attr_str_lines[0])
            else:
                # print(getattr(self, "_%s_value_" % attr.name))
                text += '* %s : <None>\n' % attr.name
        return text

    def __repr__(self):  # TODO: Improve
        attrs = []

        for attr in self._get_filtered_attribute_list():
            attrs.append(f"{attr.name}: {repr(getattr(self, '_%s_value_' % attr.name, None))}")

        return f"<{self.__class__.__name__} {{{', '.join(attrs)}}}>"

    def _log_struct(self, stream, attr):
        val = getattr(self, "_%s_value_" % attr.name)  # debug
        if not isinstance(val, BasicBase):  # debug
            # TODO: DEBUG
            self.logger.warning(val.__class__.__name__ + ":" + attr.name)
            self.logger.debug(val.__class__.__name__ + ":" + attr.name)
        else:
            try:
                out = val.get_value()  # debug
            except Exception:
                pass
            else:
                offset = stream.tell()
                hex_ver = "0x%08X" % offset
                # TODO: DEBUG
                self.logger.warning(
                    "* {0}.{1} = {2} : type {3} at {4} offset {5} - ".format(self.__class__.__name__, attr.name,
                                                                             str(out), attr.type_, hex_ver,
                                                                             offset))  # debug
                self.logger.debug(
                    "* {0}.{1} = {2} : type {3} at {4} offset {5} - ".format(self.__class__.__name__, attr.name,
                                                                             str(out), attr.type_, hex_ver,
                                                                             offset))  # debug

    def read(self, stream, data):
        """Read structure from stream."""

        self._items.clear()
        for attr in self._get_filtered_attribute_list(data, report_duplicates=True):  # We must update the attributes as we read
            # things that can only be determined at runtime (rt_xxx)
            rt_type = attr.type_ if attr.type_ != type(None) else self._template
            rt_template = attr.template if attr.template != type(None) else self._template
            rt_arg = attr.arg.eval(self) if attr.arg is not None else None

            # instantiate the class, handling arrays at the same time
            if attr.length is None:
                attr_instance = rt_type(
                    template=rt_template, argument=rt_arg,
                    parent=self)
                if attr.default is not None:
                    attr_instance.set_value(attr.default)
            elif attr.width is None:
                attr_instance = Array(
                    name=attr.name,
                    element_type=rt_type,
                    element_type_template=rt_template,
                    element_type_argument=rt_arg,
                    length=attr.length,
                    parent=self)
            else:
                attr_instance = Array(
                    name=attr.name,
                    element_type=rt_type,
                    element_type_template=rt_template,
                    element_type_argument=rt_arg,
                    length=attr.length, width=attr.width,
                    parent=self)

            # skip abstract attributes
            if attr.is_abstract:
                continue

            # assign attribute value
            setattr(self, "_%s_value_" % attr.name, attr_instance)
            attr_instance.read(stream, data)
            self._log_struct(stream, attr)  # Log after read, that way we have data after read

            # add instance to item list
            self._items.append(attr_instance)

    def write(self, stream, data):
        """Write structure to stream."""
        # write all attributes
        for attr in self._get_filtered_attribute_list(data):
            # skip abstract attributes
            if attr.is_abstract:
                continue
            # get attribute argument (can only be done at runtime)
            rt_arg = attr.arg.eval(self) if attr.arg is not None else None
            # write the attribute
            attr_value = getattr(self, "_%s_value_" % attr.name)
            attr_value.arg = rt_arg
            getattr(self, "_%s_value_" % attr.name).write(stream, data)  # TODO: Why the duplicate getattr?
            self._log_struct(stream, attr)

    def fix_links(self, data):
        """Fix links in the structure."""
        # parse arguments
        # fix links in all attributes
        for attr in self._get_filtered_attribute_list(data):
            # check if there are any links at all, commonly this speeds things up considerably
            if not attr.type_._has_links:
                continue
            self.logger.debug("fixlinks %s" % attr.name)
            # fix the links in the attribute
            getattr(self, "_%s_value_" % attr.name).fix_links(data)

    def get_links(self, data=None):
        """Get list of all links in the structure."""
        # get all links
        links = []
        for attr in self._get_filtered_attribute_list(data):
            # check if there are any links at all, this speeds things up considerably
            if not attr.type_._has_links:
                continue
            # extend list of links
            links.extend(
                getattr(self, "_" + attr.name + "_value_").get_links(data))
        # return the list of all links in all attributes
        return links

    def get_strings(self, data):
        """Get list of all strings in the structure."""
        # get all strings
        strings = []
        for attr in self._get_filtered_attribute_list(data):
            # check if there are any strings at all, this speeds things up considerably
            if (not attr.type_ is type(None)) and (not attr.type_._has_strings):
                continue
            # extend list of strings
            strings.extend(
                getattr(self, "_%s_value_" % attr.name).get_strings(data))
        # return the list of all strings in all attributes
        return strings

    def get_refs(self, data=None):
        """Get list of all references in the structure. Refs are
        links that point down the tree. For instance, if you need to parse
        the whole tree starting from the root you would use get_refs and not
        get_links, as get_links could result in infinite recursion."""
        # get all refs
        refs = []
        for attr in self._get_filtered_attribute_list(data):
            # check if there are any links at all
            # (this speeds things up considerably)
            if attr.type_ is not type(None) and not attr.type_._has_links:
                continue
            # extend list of refs
            refs.extend(
                getattr(self, "_%s_value_" % attr.name).get_refs(data))
        # return the list of all refs in all attributes
        return refs

    def get_size(self, data=None):
        """Calculate the structure size in bytes."""
        # calculate size
        size = 0
        for attr in self._get_filtered_attribute_list(data):
            # skip abstract attributes
            if attr.is_abstract:
                continue
            size += getattr(self, "_%s_value_" % attr.name).get_size(data)
        return size

    def get_hash(self, data=None):
        """Calculate a hash for the structure, as a tuple."""
        # calculate hash
        hsh = []
        for attr in self._get_filtered_attribute_list(data):
            hsh.append(
                getattr(self, "_%s_value_" % attr.name).get_hash(data))
        return tuple(hsh)

    def replace_global_node(self, oldbranch, newbranch, **kwargs):
        for attr in self._get_filtered_attribute_list():
            # check if there are any links at all
            # (this speeds things up considerably)
            if not attr.type_._has_links:
                continue
            getattr(self, "_%s_value_" % attr.name).replace_global_node(
                oldbranch, newbranch, **kwargs)

    @classmethod
    def get_games(cls):
        """Get games for which this block is supported."""
        return list(cls._games.keys())

    @classmethod
    def get_versions(cls, game):
        """Get versions supported for C{game}."""
        return cls._games[game]

    @classmethod
    def _get_attribute_list(cls):
        """Calculate the list of all attributes of this structure."""
        # string of attributes of base classes of cls
        attrs = []
        for base in cls.__bases__:
            try:
                attrs.extend(base._get_attribute_list())
            except AttributeError:  # when base class is "object"
                pass
        attrs.extend(cls._attrs)
        return attrs

    @classmethod
    def _get_names(cls):
        """Calculate the list of all attributes names in this structure.
        Skips duplicate names."""
        # string of attributes of base classes of cls
        names = []
        for base in cls.__bases__:
            try:
                names.extend(base._get_names())
            except AttributeError:  # when base class is "object"
                pass
        for attr in cls._attrs:
            if attr.name in names:
                continue
            else:
                names.append(attr.name)
        return names

    def _get_filtered_attribute_list(self, data=None, report_duplicates=False):
        """Generator for listing all 'active' attributes, that is,
        attributes whose condition evaluates ``True``, whose version
        interval contains C{version}, and whose user version is
        C{user_version}. ``None`` for C{version} or C{user_version} means
        that these checks are ignored. Duplicate names are skipped as
        well.

        Note: version and user_version arguments are deprecated, use
        the data argument instead.
        """
        if data is not None:
            version = data.version
            user_version = data.user_version
        else:
            version = None
            user_version = None

        names = set()
        for attr in self._attribute_list:
            # print(attr.name, version, attr.since, attr.until) # debug

            # check version
            if version is not None:
                if attr.since is not None and version < attr.since:
                    continue
                if attr.until is not None and version > attr.until:
                    continue
            # print("version check passed") # debug

            # check user version
            if attr.userver is not None and user_version is not None and user_version != attr.userver:
                continue
            # print("user version check passed") # debug

            # check conditions
            if attr.cond is not None and not attr.cond.eval(self):
                continue
            # print("condition passed") # debug

            if version is not None and user_version is not None and attr.vercond is not None:
                if not attr.vercond.eval(data):
                    continue
            # print("version condition passed") # debug

            # skip duplicate names
            if attr.name in names:
                if report_duplicates:
                    logging.getLogger().warning("Duplicate attribute %s was found: %s", attr.name, attr)  # TODO: More Verbose
                continue
            names.add(attr.name)
            # print("duplicate check passed") # debug

            # passed all tests
            # so yield the attribute
            yield attr

    def get_attribute(self, name):
        """Get a (non-basic) attribute."""
        return getattr(self, "_" + name + "_value_")

    # important note: to apply partial(set_attribute, name = 'xyz') the
    # name argument must be last
    def set_attribute(self, value, name):
        """Set a (non-basic) attribute."""
        # check class
        attr = getattr(self, "_" + name + "_value_")
        if attr.__class__ is not value.__class__:
            raise TypeError("expected %s but got %s"
                            % (attr.__class__.__name__,
                               value.__class__.__name__))
        # set it
        setattr(self, "_" + name + "_value_", value)

    def get_basic_attribute(self, name):
        """Get a basic attribute."""
        return getattr(self, "_" + name + "_value_").get_value()

    # important note: to apply partial(set_attribute, name = 'xyz') the
    # name argument must be last
    def set_basic_attribute(self, value, name):
        """Set the value of a basic attribute."""
        getattr(self, "_" + name + "_value_").set_value(value)

    def get_template_attribute(self, name):
        """Get a template attribute."""
        try:
            return self.get_basic_attribute(name)
        except AttributeError:
            return self.get_attribute(name)

    # important note: to apply partial(set_attribute, name = 'xyz') the
    # name argument must be last
    def set_template_attribute(self, value, name):
        """Set the value of a template attribute."""
        try:
            self.set_basic_attribute(value, name)
        except AttributeError:
            self.set_attribute(value, name)

    def tree(self):
        """A generator for parsing all blocks in the tree (starting from and
        including C{self}). By default, there is no tree structure, so returns
        self."""
        # return self
        yield self

    def update_version(self, data):
        """

        :param data:
        :return:
        """
        self._update_attributes(data)

    @staticmethod
    def _is_same_attr_type(attr_inst, attr):
        if attr_inst is None:
            return False
        if isinstance(attr, Array) and isinstance(attr_inst, Array):
            return type(attr._elementType) is type(attr_inst._elementType)
        return type(attr) is type(attr_inst)

    def _update_attributes(self, data):  # TODO: Only replace different attributes and convert in between
        self._items.clear()
        for attr in self._get_filtered_attribute_list(data, report_duplicates=True, skip_condition=True):  # skip_condition is failing fallout 4
            logging.getLogger().warning("Updating ATTR %s (%s)", attr.name, attr.type_)
            # things that can only be determined at runtime (rt_xxx)
            rt_type = attr.type_ if attr.type_ != type(None) else self._template
            rt_template = attr.template if attr.template != type(None) else self._template
            rt_arg = attr.arg.eval(self) if attr.arg is not None else None

            # instantiate the class, handling arrays at the same time
            if attr.length is None:
                attr_instance = rt_type(
                    template=rt_template, argument=rt_arg,
                    parent=self)
                if attr.default is not None:
                    attr_instance.set_value(attr.default)
            elif attr.width is None:
                attr_instance = Array(
                    name=attr.name,
                    element_type=rt_type,
                    element_type_template=rt_template,
                    element_type_argument=rt_arg,
                    length=attr.length,
                    parent=self)
            else:
                attr_instance = Array(
                    name=attr.name,
                    element_type=rt_type,
                    element_type_template=rt_template,
                    element_type_argument=rt_arg,
                    length=attr.length, width=attr.width,
                    parent=self)

            orig_attr_inst = getattr(self, "_%s_value_" % attr.name, None)
            if orig_attr_inst is not None:
                if self._is_same_attr_type(orig_attr_inst, attr_instance):
                    logging.getLogger().warning("IS SAME TYPE: %s ; %s - %s", attr.name, type(attr_instance), type(orig_attr_inst))
                    continue
                else:
                    pass  # TODO: Look into converting previous values

            # assign attribute value
            setattr(self, "_%s_value_" % attr.name, attr_instance)
            logging.getLogger().warning("Set attr %s to %s", attr.name, attr.type_)

            # add instance to item list
            self._items.append(attr_instance)

    # DetailNode

    def get_detail_child_nodes(self, edge_filter=EdgeFilter()):
        """Yield children of this structure."""
        return (item for item in self._items)

    def get_detail_child_names(self, edge_filter=EdgeFilter()):
        """Yield names of the children of this structure."""
        return (name for name in self._names)

    # GlobalNode

    def get_global_display(self):
        """Construct a convenient name for the block itself."""
        return pyffi.object_models.common._as_str(self.name) if hasattr(self, "name") else ""

    def get_global_child_nodes(self, edge_filter=EdgeFilter()):
        # TODO replace get_refs with a generator as well
        for branch in self.get_refs():
            yield branch


from pyffi.object_models.niftoolsxml.array import Array
from pyffi.object_models.niftoolsxml import BitStructBase
