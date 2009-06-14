"""This module provides a base class and a metaclass for parsing an XSD
schema and providing an interface for writing XML files that follow this
schema.
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
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

import logging
import os.path
import sys
import time
import xml.sax

import pyffi.object_models

class MetaFileFormat(pyffi.object_models.MetaFileFormat):
    """The MetaFileFormat metaclass transforms the XSD description of a
    xml format into a bunch of classes which can be directly used to
    manipulate files in this format.

    The actual implementation of the parser is delegated to
    L{XsdSaxHandler}.
    """

    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare DaeFormat to have metaclass
        MetaFileFormat, so upon creation of the DaeFormat class,
        the __init__ function is called, with

        :param cls: The class created using MetaFileFormat, for example
            DaeFormat.
        :param name: The name of the class, for example 'DaeFormat'.
        :param bases: The base classes, usually (object,).
        :param dct: A dictionary of class attributes, such as 'xsdFileName'.
        """
        super(MetaFileFormat, cls).__init__(name, bases, dct)

        # open XSD file
        xsdfilename = dct.get('xsdFileName')
        if xsdfilename:
            # set up XSD parser
            parser = xml.sax.make_parser()
            parser.setContentHandler(XsdSaxHandler(cls, name, bases, dct))

            # open XSD file
            xsdfile = cls.openfile(xsdfilename, cls.xsdFilePath)

            # parse the XSD file: control is now passed on to XsdSaxHandler
            # which takes care of the class creation
            cls.logger.debug("Parsing %s and generating classes." % xsdfilename)
            start = time.clock()
            try:
                parser.parse(xsdfile)
            finally:
                xsdfile.close()
            cls.logger.debug("Parsing finished in %.3f seconds." % (time.clock() - start))

class FileFormat(pyffi.object_models.FileFormat):
    """This class can be used as a base class for file formats. It implements
    a number of useful functions such as walking over directory trees and a
    default attribute naming function.
    """
    __metaclass__ = MetaFileFormat
    xsdFileName = None #: Override.
    xsdFilePath = None #: Override.
    logger = logging.getLogger("pyffi.object_models.xsd")

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xsd file, into a name usable
        by python.

        :param name: The attribute name.
        :type name: str
        :return: Reformatted attribute name, useable by python.

        >>> FileFormat.nameAttribute('tHis is A Silly naME')
        'this_is_a_silly_name'
        """

        # str(name) converts name to string in case name is a unicode string
        parts = str(name).replace(":", "_").split()
        return "_".join(part.lower() for part in parts)

    @staticmethod
    def nameClass(name):
        """Converts a class name, as in the xsd file, into a name usable
        by python.

        :param name: The class name.
        :type name: str
        :return: Reformatted class name, useable by python.

        >>> FileFormat.nameClass('this IS a sillyNAME')
        'ThisISASillyNAME'
        """

        # str(name) converts name to string in case name is a unicode string
        partss = [part.split("_") for part in str(name).split()]
        attrname = ""
        for parts in partss:
            for part in parts:
                attrname += part[0].upper() + part[1:]
        return attrname

class Fixed(object):
    """A class whose attributes are fixed.

    >>> class X(Fixed):
    ...     test = 0
    >>> x = X()
    >>> x.test
    0
    >>> x.test = 5
    >>> x.test
    5
    >>> x.newattr = 7 # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    AttributeError: ...
    """
    def __setattr__(self, name, value):
        if name not in self.__class__.__dict__:
            raise AttributeError("Cannot set attribute '%s'." % name)
        object.__setattr__(self, name, value)

class XsdMetaAttribute(Fixed):
    class Use:
        OPTIONAL = 0
        PROHIBITED = 1
        REQUIRED = 2
    # common
    default = None
    fixed = None
    form = None
    id_ = None
    name = None
    ref = None
    type_ = None
    annotation = None
    simple_type = None
    # in attributes only
    use = Use.OPTIONAL
    # in elements only
    abstract = False
    block = None
    final = None
    nillable = False
    substitution_group = None
    complex_type = None
    unique = None
    key = None
    keyref = None
    # in groups only
    all_ = None
    choice = None
    sequence = None
    # in elements and in groups only
    max_occurs = 1
    min_occurs = 1

class XsdMetaClass(Fixed):
    # common
    final = None
    id_ = None
    name = None
    annotation = None
    # in simple types only
    restriction = None
    list_ = None
    union = None
    # in complex types only
    abstract = False
    block = None
    mixed = False
    simple_content = None
    complex_content = None
    group = None
    all_ = None
    choice = None
    sequence = None
    attributes = []
    # our attributes
    _fullname = None # for instance: grandparent.parent.name

class XsdError(StandardError):
    """The XSD handler will throw this exception if something goes wrong while
    parsing."""
    pass

class XsdSaxHandler(xml.sax.handler.ContentHandler):
    """This class contains all functions for parsing the xsd and converting
    the schema into Python classes."""
    # xsd elements
    # (see http://www.w3.org/TR/xmlschema-0/#indexEl)
    tagAll = 1
    tagAnnotation = 2
    tagAny = 3
    tagAnyAttribute = 4
    tagAppinfo = 5
    tagAttribute = 6
    tagAttributeGroup = 7
    tagChoice = 8
    tagComplexContent = 9
    tagComplexType = 10
    tagDocumentation = 11
    tagElement = 12
    tagEnumeration = 13
    tagExtension = 14
    tagField = 15
    tagGroup = 16
    tagImport = 17
    tagInclude = 18
    tagKey = 19
    tagKeyref = 20
    tagLength = 21
    tagList = 22
    tagMaxInclusive = 23
    tagMaxLength = 24
    tagMinInclusive = 25
    tagMinLength = 26
    tagPattern = 27
    tagRedefine = 28
    tagRestriction = 29
    tagSchema = 30
    tagSelector = 31
    tagSequence = 32
    tagSimpleContent = 33
    tagSimpleType = 34
    tagUnion = 35
    tagUnique = 36

    # these tags are not listed in the official docs, but they are used
    tagMaxExclusive = 100

    tags = {
        "all": tagAll,
        "annotation": tagAnnotation,
        "any": tagAny,
        "anyAttribute": tagAnyAttribute,
        "appinfo": tagAppinfo,
        "attribute": tagAttribute,
        "attributeGroup": tagAttributeGroup,
        "choice": tagChoice,
        "complexContent": tagComplexContent,
        "complexType": tagComplexType,
        "documentation": tagDocumentation,
        "element": tagElement,
        "enumeration": tagEnumeration,
        "extension": tagExtension,
        "field": tagField,
        "group": tagGroup,
        "import": tagImport,
        "include": tagInclude,
        "key": tagKey,
        "keyref": tagKeyref,
        "length": tagLength,
        "list": tagList,
        "maxInclusive": tagMaxInclusive,
        "maxLength": tagMaxLength,
        "minInclusive": tagMinInclusive,
        "minLength": tagMinLength,
        "pattern": tagPattern,
        "redefine": tagRedefine,
        "restriction": tagRestriction,
        "schema": tagSchema,
        "selector": tagSelector,
        "sequence": tagSequence,
        "simpleContent": tagSimpleContent,
        "simpleType": tagSimpleType,
        "union": tagUnion,
        "unique": tagUnique,
        "maxExclusive": tagMaxExclusive}

    # xsd attributes
    # (see http://www.w3.org/TR/xmlschema-0/#indexAttr)
    attrAbstract = 1
    attrAttributeFormDefault = 2
    attrBase = 3
    attrBlock = 4
    attrBlockDefault = 5
    attrDefault = 6
    attrElementFormDefault = 7
    attrFinal = 8
    attrFinalDefault = 9
    attrFixed = 10
    attrForm = 11
    attrItemType = 12
    attrMemberTypes = 13
    attrMaxOccurs = 14
    attrMinOccurs = 15
    attrMixed = 16
    attrName = 17
    attrNamespace = 18
    attrXsiNoNamespaceSchemaLocation = 19
    attrXsiNil = 20
    attrNillable = 21
    attrProcessContents = 22
    attrRef = 23
    attrSchemaLocation = 24
    attrXsiSchemaLocation = 25
    attrSubstitutionGroup = 26
    attrTargetNamespace = 27
    attrType = 28
    attrXsiType = 29
    attrUse = 30
    attrXpath = 31

    attrs = {
        "abstract": attrAbstract,
        "attributeFormDefault": attrAttributeFormDefault,
        "base": attrBase,
        "block": attrBlock,
        "blockDefault": attrBlockDefault,
        "default": attrDefault,
        "elementFormDefault": attrElementFormDefault,
        "final": attrFinal,
        "finalDefault": attrFinalDefault,
        "fixed": attrFixed,
        "form": attrForm,
        "itemType": attrItemType,
        "memberTypes": attrMemberTypes,
        "maxOccurs": attrMaxOccurs,
        "minOccurs": attrMinOccurs,
        "mixed": attrMixed,
        "name": attrName,
        "namespace": attrNamespace,
        "xsi:noNamespaceSchemaLocation": attrXsiNoNamespaceSchemaLocation,
        "xsi:nil": attrXsiNil,
        "nillable": attrNillable,
        "processContents": attrProcessContents,
        "ref": attrRef,
        "schemaLocation": attrSchemaLocation,
        "xsi:schemaLocation": attrXsiSchemaLocation,
        "substitutionGroup": attrSubstitutionGroup,
        "targetNamespace": attrTargetNamespace,
        "type": attrType,
        "xsi:type": attrXsiType,
        "use": attrUse,
        "xpath": attrXpath}

    def __init__(self, cls, name, bases, dct):
        """Set up the xsd parser."""
        # initialize base class (no super because old style base class)
        xml.sax.handler.ContentHandler.__init__(self)

        # xsd prefix (this is set if the first element is read)
        self.prefix = None

        # save dictionary for future use
        self.dct = dct

        # initialize tag and class stack
        self.tag_stack = []
        self.class_stack = []
        self.attr_stack = []
        # keep track last element of self.tag_stack and self.class_stack
        # storing this reduces overhead as profiling has shown
        self.current_tag = None
        self.current_attr = None
        self.current_class = None

        # cls needs to be accessed in member functions, so make it an instance
        # member variable
        self.cls = cls

        # dictionary for attributes of every class
        # maps each class full name to a list of attributes
        # the "" class is used for global attributes
        self.class_attrs_dict = {"": []}

    def push_tag(self, tag):
        """Push tag on the stack and make it the current tag.

        :param tag: The tag to put on the stack.
        :type tag: int
        """
        self.tag_stack.insert(0, tag)
        self.current_tag = tag

    def pop_tag(self):
        """Pop the current tag from the stack and return it. Also update
        the current tag.

        :return: The tag popped from the stack.
        """
        lasttag = self.tag_stack.pop(0)
        try:
            self.current_tag = self.tag_stack[0]
        except IndexError:
            self.current_tag = None
        return lasttag

    def push_attr(self, attr):
        """Push attribute on the stack and make it the current attribute.
        The attribute is also automatically added to the current class
        attribute.

        :param attr: The attribute to put on the stack.
        :type attr: XXX
        """
        if not self.class_stack:
            if (self.current_tag != self.tagSchema):
                self.cls.logger.warn(
                    "No current class, but current tag is not schema "
                    "(it is %i)" % self.current_tag)
            klass = None
            fullname = ""
        else:
            klass = self.class_stack[-1]
            fullname = klass._meta._fullname
        self.cls.logger.debug("attribute %s.%s" % (fullname, attr.name))
        self.attr_stack.append(attr)
        self.current_attr = attr
        # TODO: check just the name
        if attr.name in (otherattr.name
                         for otherattr in self.class_attrs_dict[fullname]):
            self.cls.logger.warn("class %s already has %s"
                                 % (fullname, attr.name))
        self.class_attrs_dict[fullname].append(attr)

    def pop_attr(self):
        """Pop the current tag from the stack and return it. Also update
        the current tag.

        :return: The tag popped from the stack.
        """
        lastattr = self.attr_stack.pop()
        try:
            self.current_attr = self.attr_stack[-1]
        except IndexError:
            self.current_attr = None
        return lastattr

    def push_class(self, meta_class):
        """Push class on the stack and make it the current one.

        :param klass: The class to put on the stack.
        :type klass: XXX
        """
        # TODO: declare classes also as attributes!! now everything is global

        # shortcut for fake class
        if meta_class is None:
            self.class_stack.append(None)
            self.current_class = None
            return
        # create class
        klass = type(meta_class.name, (),
                     {"_meta": meta_class,
                      "__module__": self.cls.__module__})
        # construct full class name
        if self.class_stack:
            klass._meta._fullname = (self.current_class._meta._fullname
                                     + "." + klass._meta.name)
        else:
            klass._meta._fullname = klass._meta.name
        self.cls.logger.debug("class %s" % klass._meta._fullname)
        # register class in self.cls and in class stack
        if self.class_stack:
            setattr(self.class_stack[-1], klass._meta.name, klass)
        else:
            setattr(self.cls, klass._meta.name, klass)
        self.class_stack.append(klass)
        # update current class
        self.current_class = klass
        # set up empty attribute list
        if klass._meta._fullname in self.class_attrs_dict:
            raise XsdError("Duplicate definition of %s." % klass._meta._fullname)
        self.class_attrs_dict[klass._meta._fullname] = []

    def pop_class(self):
        """Pop the current class from the stack."""
        lastclass = self.class_stack.pop()
        try:
            self.current_class = self.class_stack[-1]
        except IndexError:
            self.current_class = None
        return lastclass

    def get_element_tag(self, name):
        """Find tag for named element.

        :param name: The name of the element, including the prefix.
        :type name: str
        :return: The tag, as integer (one of the tagXxx constants).
        """
        # find prefix
        # the prefix can be anything; see comments under the example
        # here: http://www.w3.org/TR/xmlschema-0/#POSchema
        if self.prefix is None:
            idx = name.find(":")
            if idx == -1:
                self.prefix = ""
            else:
                self.prefix = name[:idx + 1]
        # check that name starts with prefix
        if not name.startswith(self.prefix):
            raise XsdError("invalid prefix on element '%s'" % name)
        # strip prefix from name
        shortname = name[len(self.prefix):]
        # get the tag identifier
        try:
            return self.tags[shortname]
        except KeyError:
            raise XsdError("invalid element '%s'" % name)

    def startElement(self, name, attrs):
        """Called when parser starts parsing an element called C{name}.

        :param name: The name of the xsd element.
        :param attrs: A dictionary of attributes of the element.
        """

        # Check the stack, if the stack does not exist then we must be
        # at the root of the xsd file, and the element must be "xsd:schema".
        # The schema element has no further attributes of interest,
        # so we can exit the function after pushing it on the stack.
        tag = self.get_element_tag(name)
        if not self.tag_stack:
            if tag != self.tagSchema:
                raise XsdError("this is not an xsd file")
            self.push_tag(tag)
            return

        # do a number of things, depending on the tag
        # self.current_tag reflects the element in which <name> is embedded
        # (it is the last element of the stack)
        if tag == self.tagAnnotation:
            # skip
            pass
        elif tag == self.tagDocumentation:
            # skip (TODO: use for docstring)
            pass
        elif tag == self.tagGroup:
            if attrs.get("name"):
                # attribute definition
                attr = XsdMetaAttribute()
                attr.name = self.cls.nameAttribute(attrs.get("name"))
                attr.type_ = self.cls.nameClass(attrs.get("name"))
                self.push_attr(attr)
                # class definition
                meta_class = XsdMetaClass()
                meta_class.name = attr.type_
                self.push_class(meta_class)
            elif attrs.get("ref"):
                # attribute definition only
                attr = XsdMetaAttribute()
                attr.name = self.cls.nameAttribute(attrs.get("ref"))
                attr.type_ = self.cls.nameClass(attrs.get("ref"))
                attr.ref = attr.name
                self.push_attr(attr)
                # push a fake class for symmetry
                self.push_class(None)
            else:
                raise XsdError(
                    "Invalid group definition: missing name and ref.")
        elif tag == self.tagElement:
            # create an attribute for the current class
            # if it has a type attribute, then the class can be taken from
            # that type, otherwise, wait for complexType or simpleType tag

            # all elements must have a declared name
            # the name is either attrs["name"] if declared, or attrs["ref"]
            attr = XsdMetaAttribute()
            attr.name = self.cls.nameAttribute(
                attrs.get("name", attrs.get("ref")))
            attr.ref = self.cls.nameAttribute(attrs.get("ref"))

            # if the type is not defined as an attribute, it must be resolved
            # later in a simpleType or complexType child, or will come from
            # the reference type
            attr.type_ = self.cls.nameClass(attrs.get("type", attr.name))
            self.push_attr(attr)
        elif tag == self.tagAttribute:
            # add an attribute to this element
            attr = XsdMetaAttribute()
            attr.name = self.cls.nameAttribute(
                attrs.get("name", attrs.get("ref")))
            attr.type_ = self.cls.nameClass(attrs.get("type", attr.name))
            self.push_attr(attr)
        elif tag in (self.tagSimpleType, self.tagComplexType):
            # create a new simple type
            # if it has a name attribute, then take that as name
            # if it has no name attribute, then it should be a child of an
            # element tag, and it makes sense to use the element name
            # as a basis for this type's name (e.g. element "quantity" with
            # simpleType child would be automatically have the class name
            # Quantity)

            # simpleType must have a name
            meta_class = XsdMetaClass()
            meta_class.name = self.cls.nameClass(
                attrs.get("name", self.current_attr.name))
            self.push_class(meta_class)
        else:
            ### uncomment this if all tags are handled 
            #raise XsdError("unhandled element %s" % name)
            pass

        # push tag on stack
        self.push_tag(tag)

    def endElement(self, name):
        """Called at the end of each xml tag.

        Creates classes.
        """
        if not self.tag_stack:
            raise XsdError("no start element for end element %s" % name)
        tag = self.get_element_tag(name)
        if self.pop_tag() != tag:
            raise XsdError("end element %s does not match start element" % name)
        elif tag == self.tagAnnotation:
            return
        elif tag == self.tagGroup:
            # close group class definition
            self.pop_class()
            # close attribute
            self.pop_attr()
        elif tag == self.tagElement:
            self.pop_attr()
        elif tag in (self.tagSimpleType, self.tagComplexType):
            self.pop_class()
        elif tag in []: # TODO
            # create class
            class_type = type(
                str(self.className), (self.classBase,), self.classDict)
            # assign it to cls.<className> if it has not been implemented
            # internally
            if not self.className in self.cls.__dict__:
                setattr(self.cls, self.className, class_type)
            # append class to the appropriate list
            if tag == self.tagStruct:
                self.cls.xmlStruct.append(class_type)
            elif tag == self.tagEnum:
                self.cls.xmlEnum.append(class_type)
            elif tag == self.tagAlias:
                self.cls.xmlAlias.append(class_type)
            elif tag == self.tagBitStruct:
                self.cls.xmlBitStruct.append(class_type)
            # reset variables
            self.className = None
            self.classDict = None
            self.classBase = None

    def endDocument(self):
        """Called when the xsd is completely parsed.

        Resolves forward references.
        """
        pass

    def characters(self, chars):
        """Parses characters."""
        pass

