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

import PyFFI.ObjectModels.FileFormat
from PyFFI import Utils

import os.path
import sys
from types import FunctionType
import xml.sax

class MetaXsdFileFormat(PyFFI.ObjectModels.FileFormat.MetaFileFormat):
    """The MetaXsdFileFormat metaclass transforms the XSD description of a
    xml format into a bunch of classes which can be directly used to
    manipulate files in this format.

    The actual implementation of the parser is delegated to
    L{XsdSaxHandler}.
    """

    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare DaeFormat to have metaclass
        MetaXsdFileFormat, so upon creation of the DaeFormat class,
        the __init__ function is called, with

        :param cls: The class created using MetaXsdFileFormat, for example
            DaeFormat.
        :param name: The name of the class, for example 'DaeFormat'.
        :param bases: The base classes, usually (object,).
        :param dct: A dictionary of class attributes, such as 'xsdFileName'.
        """
        super(MetaXsdFileFormat, cls).__init__(name, bases, dct)

        # consistency checks
        if not 'xsdFileName' in dct:
            raise TypeError("class %s : missing xsdFileName attribute" % cls)

        # set up XML parser
        parser = xml.sax.make_parser()
        parser.setContentHandler(XsdSaxHandler(cls, name, bases, dct))

        # open XSD file
        if not 'xsdFilePath' in dct:
            xsdfile = open(dct['xsdFileName'])
        else:
            for filepath in dct['xsdFilePath']:
                if not filepath:
                    continue
                try:
                    xsdfile = open(os.path.join(filepath, dct['xsdFileName']))
                except IOError:
                    continue
                break
            else:
                raise IOError("'%s' not found in any of the directories %s"%(
                    dct['xsdFileName'], dct['xsdFilePath']))

        # parse the XSD file: control is now passed on to XsdSaxHandler
        # which takes care of the class creation
        try:
            parser.parse(xsdfile)
        finally:
            xsdfile.close()

class XsdFileFormat(PyFFI.ObjectModels.FileFormat.FileFormat):
    """This class can be used as a base class for file formats. It implements
    a number of useful functions such as walking over directory trees and a
    default attribute naming function.
    """

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xsd file, into a name usable
        by python.

        :param name: The attribute name.
        :type name: str
        :return: Reformatted attribute name, useable by python.

        >>> XsdFileFormat.nameAttribute('tHis is A Silly naME')
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

        >>> XsdFileFormat.nameClass('this IS a sillyNAME')
        'ThisISASillyNAME'
        """

        # str(name) converts name to string in case name is a unicode string
        partss = [part.split("_") for part in str(name).split()]
        attrname = ""
        for parts in partss:
            for part in parts:
                attrname += part[0].upper() + part[1:]
        return attrname

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
        self.stack = []
        self.classstack = ()
        self.attrstack = []
        # keep track last element of self.stack and self.classstack
        # storing this reduces overhead as profiling has shown
        self.currentTag = None
        self.currentAttr = None

        # cls needs to be accessed in member functions, so make it an instance
        # member variable
        self.cls = cls

        # dictionary for attributes of every class
        # maps each class to a list of attributes
        # the "None" class is used for global attributes
        self.classAttributes = {(): []}

    def pushTag(self, tag):
        """Push tag on the stack and make it the current tag.

        :param tag: The tag to put on the stack.
        :type tag: int
        """
        self.stack.insert(0, tag)
        self.currentTag = tag

    def popTag(self):
        """Pop the current tag from the stack and return it. Also update
        the current tag.

        :return: The tag popped from the stack.
        """
        lasttag = self.stack.pop(0)
        try:
            self.currentTag = self.stack[0]
        except IndexError:
            self.currentTag = None
        return lasttag

    def pushAttr(self, attr):
        """Push attribute on the stack and make it the current attribute.
        The attribute is also automatically added to the current class
        attribute.

        :param attr: The attribute to put on the stack.
        :type attr: XXX
        """
        if self.classstack == ():
            if (self.currentTag != self.tagSchema):
                print("WARNING: no current class, but current tag is not \
schema (it is %i)" % self.currentTag)
        # DEBUG
        #print("attribute %s.%s" % (".".join(self.classstack), attr))
        attrinfo = [attr] # TODO: make this a self-contained class
        self.attrstack.insert(0, attrinfo)
        self.currentAttr = attrinfo
        # TODO: check just the name
        #if attrinfo in self.classAttributes[self.classstack]:
        #    print("WARNING: class %s already has %s"
        #          % (".".join(self.classstack), attr))
        self.classAttributes[self.classstack].append(attrinfo)

    def popAttr(self):
        """Pop the current tag from the stack and return it. Also update
        the current tag.

        :return: The tag popped from the stack.
        """
        lastattr = self.attrstack.pop(0)
        try:
            self.currentAttr = self.attrstack[0]
        except IndexError:
            self.currentAttr = None
        return lastattr

    def pushClass(self, klass):
        """Push class on the stack and make it the current one.

        :param klass: The class to put on the stack.
        :type klass: XXX
        """
        # TODO: declare classes also as attributes!! now everything is global
        self.classstack = self.classstack + (klass,)
        # DEBUG
        #print("class %s" % (".".join(self.classstack)))
        # set up empty attribute list
        self.classAttributes[self.classstack] = []

    def popClass(self):
        """Pop the current class from the stack."""
        self.classstack = self.classstack[:-1]

    def getElementTag(self, name):
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
        tag = self.getElementTag(name)
        if not self.stack:
            if tag != self.tagSchema:
                raise XsdError("this is not an xsd file")
            self.pushTag(tag)
            return

        # do a number of things, depending on the tag
        # self.currentTag reflects the element in which <name> is embedded
        # (it is the last element of the stack)
        if tag == self.tagAnnotation:
            # skip
            pass
        elif tag == self.tagDocumentation:
            # skip (TODO: use for docstring)
            pass
        elif tag in (self.tagElement, self.tagGroup):
            # create an attribute for the current class
            # - if it has a type attribute, then the class can be taken from
            #   that type, otherwise, wait for complexType or simpleType tag
            # - if the element has a parent, then add it to the parent list of
            #   attributes, if not, add its type to the list of possible root
            #   objects

            # all elements must have a declared name
            # the name is either attrs["name"] if declared, or attrs["ref"]
            # (remove __BUG__ once everything works!)
            elemname = self.cls.nameAttribute(
                attrs.get("name", attrs.get("ref", "__BUG__")))

            # if the type is not defined as an attribute, it must be resolved
            # later in a simpleType or complexType child
            typename = self.cls.nameClass(
                attrs.get("type", self.cls.nameClass(elemname)))

            self.pushAttr(elemname)
            self.currentAttr.append(typename)
            if tag == self.tagGroup:
                self.pushClass(typename)
        elif tag == self.tagAttribute:
            # add an attribute to this element
            attrname = self.cls.nameAttribute(
                attrs.get("name", attrs.get("ref", "__BUG__")))
            typename = self.cls.nameClass(
                attrs.get("type", self.cls.nameClass(attrname)))
            self.pushAttr(attrname)
            self.currentAttr.append(typename)
        elif tag in (self.tagSimpleType, self.tagComplexType):
            # create a new simple type
            # if it has a name attribute, then take that as name
            # if it has no name attribute, then it should be a child of an
            # element tag, and it makes sense to use the element name
            # as a basis for this type's name (e.g. element "quantity" with
            # simpleType child would be automatically have the class name
            # QuantityType)

            # simpleType must have a name
            typename = self.cls.nameClass(
                attrs.get("name", self.currentAttr[0]))
            self.pushClass(typename)
        else:
            ### uncomment this if all tags are handled 
            #raise XsdError("unhandled element %s" % name)
            pass

        # push tag on stack
        self.pushTag(tag)

    def endElement(self, name):
        """Called at the end of each xml tag.

        Creates classes.
        """
        if not self.stack:
            raise XsdError("no start element for end element %s" % name)
        tag = self.getElementTag(name)
        if self.popTag() != tag:
            raise XsdError("end element %s does not match start element" % name)
        elif tag == self.tagAnnotation:
            return
        elif tag in (self.tagElement, self.tagGroup):
            self.popAttr()
            if tag == self.tagGroup:
                self.popClass()
        elif tag in (self.tagSimpleType, self.tagComplexType):
            self.popClass()
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

