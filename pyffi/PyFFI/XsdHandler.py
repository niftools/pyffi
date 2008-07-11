"""Parses XML Schema Definition (XSD) file and set up representation of
the XML schema as a bunch of classes."""

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

import xml.sax
from types import NoneType, FunctionType, TypeType
import sys

class XsdError(StandardError):
    """The XSD handler will throw this exception if something goes wrong while
    parsing."""
    pass

class XsdSaxHandler(object, xml.sax.handler.ContentHandler):
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
        # initialize base class
        super(XsdSaxHandler, self).__init__()

        # xsd prefix (this is set if the first element is read)
        self.prefix = None

        # save dictionary for future use
        self.dct = dct

        # initialize tag and class stack
        self.stack = []
        self.classstack = []
        self.attrstack = []
        # keep track last element of self.stack and self.classstack
        # storing this reduces overhead as profiling has shown
        self.currentTag = None
        self.currentClass = None
        self.currentAttr = None

        # cls needs to be accessed in member functions, so make it an instance
        # member variable
        self.cls = cls

        # dictionary for attributes of every class
        # maps each class to a list of attributes
        # the "None" class is used for global attributes
        self.classAttributes = {None: []}

    def pushTag(self, tag):
        """Push tag on the stack and make it the current tag.

        @param tag: The tag to put on the stack.
        @type tag: int
        """
        self.stack.insert(0, tag)
        self.currentTag = tag

    def popTag(self):
        """Pop the current tag from the stack and return it. Also update
        the current tag.

        @return: The tag popped from the stack.
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

        @param attr: The attribute to put on the stack.
        @type attr: XXX
        """
        print("registering attribute %s.%s" % (self.currentClass, attr))
        if self.currentClass == None:
            if (self.currentTag != self.tagSchema):
                print("WARNING: no current class, but current tag is not \
schema (it is %i)" % self.currentTag)
        attrinfo = [attr] # TODO: make this a self-contained class
        self.attrstack.insert(0, attrinfo)
        self.currentAttr = attrinfo
        # TODO: check just the name
        #if attrinfo in self.classAttributes[self.currentClass]:
        #    print("WARNING: class %s already has %s"
        #          % (self.currentClass, attr))
        self.classAttributes[self.currentClass].append(attrinfo)

    def popAttr(self):
        """Pop the current tag from the stack and return it. Also update
        the current tag.

        @return: The tag popped from the stack.
        """
        lastattr = self.attrstack.pop(0)
        try:
            self.currentAttr = self.attrstack[0]
        except IndexError:
            self.currentAttr = None
        return lastattr

    def pushClass(self, klass):
        """Push class on the stack and make it the current one.

        @param klass: The class to put on the stack.
        @type klass: XXX
        """
        # TODO: declare classes also as attributes!! now everything is global
        print("registering class %s" % klass)
        if self.currentClass == None:
            if (self.currentTag != self.tagSchema):
                print("WARNING: current tag is not schema, but %i" % self.currentTag)
        self.classstack.insert(0, klass)
        self.currentClass = klass
        # set up empty attribute list
        if klass in self.classAttributes:
            # TODO: if everything is sorted out, make this raise an exception
            print("WARNING: class %s already defined" % klass)
        self.classAttributes[klass] = []

    def popClass(self):
        """Pop the current class from the stack and return it. Also update
        the current class.

        @return: The class popped from the stack.
        """
        lastclass = self.classstack.pop(0)
        try:
            self.currentClass = self.classstack[0]
        except IndexError:
            self.currentClass = None
        return lastclass

    def getElementTag(self, name):
        """Find tag for named element.

        @param name: The name of the element, including the prefix.
        @type name: str
        @return: The tag, as integer (one of the tagXxx constants).
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

        @param name: The name of the xsd element.
        @param attrs: A dictionary of attributes of the element.
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
            elemname = attrs.get("name", attrs.get("ref", "__BUG__"))

            # if the type is not defined as an attribute, it must be resolved
            # later in a simpleType or complexType child
            typename = attrs.get("type", "__RESOLVE:%sType__" % elemname)

            self.pushAttr(elemname)
            self.currentAttr.append(typename)
        elif tag == self.tagAttribute:
            # add an attribute to this element
            pass
        elif tag in (self.tagSimpleType, self.tagComplexType):
            # create a new simple type
            # if it has a name attribute, then take that as name
            # if it has no name attribute, then it should be a child of an
            # element tag, and it makes sense to use the element name
            # as a basis for this type's name (e.g. element "quantity" with
            # simpleType child would be automatically have the class name
            # QuantityType)

            # simpleType must have a name
            typename = attrs.get("name", "%sType" % self.currentAttr[0])
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

        Searches and adds class customized functions.
        """
        for obj in self.cls.__dict__.values():
            # skip objects that are not generated by the C{type} function
            # or that do not derive from the base class
            if not (isinstance(obj, TypeType) and issubclass(obj, object)):
                continue

            # add custom functions to interface
            # first find the module
            oldsyspath = sys.path
            # note: keep the old sys.path because the customize modules might
            # import other modules (such as math)
            sys.path = [self.dct['clsFilePath']] + sys.path
            try:
                # import custom object module
                mod = __import__(obj.__name__, globals(),  locals(), [])
            except ImportError, err:
                if str(err) != "No module named " + obj.__name__:
                    raise
                else:
                    continue
            finally:
                sys.path = oldsyspath
            # set object's cls argument to give it access to other objects
            # defined in self.cls
            obj.cls = self.cls
            # iterate over all objects defined in the module
            for objname, objfunc in mod.__dict__.items():
                # skip if it is not a function
                if not isinstance(objfunc, FunctionType):
                    continue
                setattr(obj, objname, objfunc)

    def characters(self, chars):
        """Parses characters."""
        pass

