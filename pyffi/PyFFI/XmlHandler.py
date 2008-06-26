"""Parses file format description in XML format and set up representation of
the file format in memory, as a bunch of classes."""

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

from PyFFI.Bases.Struct     import StructBase
from PyFFI.Bases.BitStruct  import BitStructBase
from PyFFI.Bases.Enum       import EnumBase
from PyFFI.Bases.Expression import Expression

class StructAttribute(object):
    """Helper class to collect attribute data of struct add tags."""

    def __init__(self, cls, attrs):
        """Initialize attribute from the xml attrs dictionary of an
        add tag.

        @param cls: The class where all types reside.
        @param attrs: The xml add tag attribute dictionary."""
        # mandatory parameters
        self.name = cls.nameAttribute(attrs["name"])
        attrs_type_str = attrs["type"]
        if attrs_type_str != "TEMPLATE":
            try:
                self.type = getattr(cls, attrs_type_str)
            except AttributeError:
                # forward declaration, resolved at endDocument
                self.type = attrs_type_str
        else:
            self.type = NoneType # type determined at runtime
        # optional parameters
        self.default = attrs.get("default")
        self.template = attrs.get("template") # resolved in endDocument
        self.arg = attrs.get("arg")
        self.arr1 = attrs.get("arr1")
        self.arr2 = attrs.get("arr2")
        self.cond = attrs.get("cond")
        self.ver1 = attrs.get("ver1")
        self.ver2 = attrs.get("ver2")
        self.userver = attrs.get("userver")
        self.doc = "" # handled in xml parser's characters function

        # post-processing
        if self.default:
            try:
                tmp = self.type()
                tmp.setValue(self.default)
                self.default = tmp.getValue()
                del tmp
            except StandardError:
                # conversion failed; not a big problem
                self.default = None
        if self.arr1:
            self.arr1 = Expression(self.arr1, cls.nameAttribute)
        if self.arr2:
            self.arr2 = Expression(self.arr2, cls.nameAttribute)
        if self.cond:
            self.cond = Expression(self.cond, cls.nameAttribute)
        if self.arg:
            try:
                self.arg = int(self.arg)
            except ValueError:
                self.arg = cls.nameAttribute(self.arg)
        if self.userver:
            self.userver = int(self.userver)
        if self.ver1:
            self.ver1 = cls.versionNumber(self.ver1)
        if self.ver2:
            self.ver2 = cls.versionNumber(self.ver2)

class BitStructAttribute(object):
    """Helper class to collect attribute data of bitstruct bits tags."""

    def __init__(self, cls, attrs):
        """Initialize attribute from the xml attrs dictionary of an
        add tag.

        @param cls: The class where all types reside.
        @param attrs: The xml add tag attribute dictionary."""
        # mandatory parameters
        self.name = cls.nameAttribute(attrs["name"])
        self.numbits = int(cls.nameAttribute(attrs["numbits"]))
        # optional parameters
        self.default = attrs.get("default")
        self.cond = attrs.get("cond")
        self.ver1 = attrs.get("ver1")
        self.ver2 = attrs.get("ver2")
        self.userver = attrs.get("userver")
        self.doc = "" # handled in xml parser's characters function

        # post-processing
        if self.default:
            self.default = int(self.default)
        if self.cond:
            self.cond = Expression(self.cond, cls.nameAttribute)
        if self.userver:
            self.userver = int(self.userver)
        if self.ver1:
            self.ver1 = cls.versionNumber(self.ver1)
        if self.ver2:
            self.ver2 = cls.versionNumber(self.ver2)

class XmlError(StandardError):
    """The XML handler will throw this exception if something goes wrong while
    parsing."""
    pass

class XmlSaxHandler(object, xml.sax.handler.ContentHandler):
    """This class contains all functions for parsing the xml and converting
    the xml structure into Python classes."""
    tagFile = 1
    tagVersion = 2
    tagBasic = 3
    tagAlias = 4
    tagEnum = 5
    tagOption = 6
    tagBitStruct = 7
    tagStruct = 8
    tagAttribute = 9
    tagBits = 10

    tags = {
    "fileformat": tagFile,
    "version": tagVersion,
    "basic": tagBasic,
    "alias": tagAlias,
    "enum": tagEnum,
    "option": tagOption,
    "bitstruct": tagBitStruct,
    "struct": tagStruct,
    "bits": tagBits,
    "add": tagAttribute}

    # for compatibility with niftools
    tags_niftools = {
    "niftoolsxml": tagFile,
    "compound": tagStruct,
    "niobject": tagStruct}

    def __init__(self, cls, name, bases, dct):
        """Set up the xml parser.

        Upon instantiation this function does the following:
          - Creates a dictionary C{cls.versions} which maps each supported
            version strings onto a version integer.
          - Creates a dictionary C{cls.games} which maps each supported game
            onto a list of versions.
          - Makes an alias C{self.cls} for C{cls}.
          - Initializes a stack C{self.stack} of xml tags.
          - Initializes the current tag.
          - Creates lists where the created classes will be stored if they
            ever need to be parsed:
              - C{self.cls.xmlEnum}
              - C{self.cls.xmlAlias}
              - C{self.cls.xmlBitStruct}
              - C{self.cls.xmlStruct}
        """
        # initialize base class
        super(XmlSaxHandler, self).__init__()

        # save dictionary for future use
        self.dct = dct

        # initialize dictionaries
        # cls.version maps each supported version string to a version number
        cls.versions = {}
        # cls.games maps each supported game to a list of header version
        # numbers
        cls.games = {}
        # note: block versions are stored in the _games attribute of the
        # struct class

        # initialize tag stack
        self.stack = []
        # keep track last element of self.stack
        # storing this reduces overhead as profiling has shown
        self.currentTag = None

        # cls needs to be accessed in member functions, so make it an instance
        # member variable
        self.cls = cls

        # We also keep an ordered list of all classes that have been created.
        # The xmlStruct list includes all xml generated struct classes,
        # including those that are replaced by a native class in cls (for
        # instance NifFormat.String). The idea is that these lists should
        # contain sufficient info from the xml so they can be used to write
        # other python scripts that would otherwise have to implement their own
        # xml parser. See makehsl.py for an example of usage.
        #
        # (note: no classes are created for basic types, so no list for those)
        self.cls.xmlEnum = []
        self.cls.xmlAlias = []
        self.cls.xmlBitStruct = []
        self.cls.xmlStruct = []

        # elements for creating new classes
        self.className = None
        self.classDict = None
        self.classBase = None

        # elements for basic classes
        self.basicClass = None

        # elements for versions
        self.versionString = None

    def pushTag(self, tag):
        """Push tag C{tag} on the stack and make it the current tag.

        @param tag: The tag to put on the stack."""
        self.stack.insert(0, tag)
        self.currentTag = tag

    def popTag(self):
        """Pop the current tag from the stack and return it. Also update
        the current tag.

        @return: The tag popped from the stack."""
        lasttag = self.stack.pop(0)
        try:
            self.currentTag = self.stack[0]
        except IndexError:
            self.currentTag = None
        return lasttag

    def startElement(self, name, attrs):
        """Called when parser starts parsing an element called C{name}.

        This function sets up all variables for creating the class
        in the C{self.endElement} function. For struct elements, it will set up
        C{self.className}, C{self.classBase}, and C{self.classDict} which
        will be used to create the class by invokation of C{type} in
        C{self.endElement}. For basic, enum, and bitstruct elements, it will
        set up C{self.basicClass} to link to the proper class implemented by
        C{self.cls}. The code also performs sanity checks on the attributes.

        For xml add tags, the function will add an entry to the
        C{self.classDict["_attrs"]} list. Note that this list is used by the
        struct metaclass: the class attributes are created exactly from this
        list.

        @param name: The name of the xml element.
        @param attrs: A dictionary of attributes of the element."""
        # get the tag identifier
        try:
            tag = self.tags[name]
        except KeyError:
            try:
                tag = self.tags_niftools[name]
            except KeyError:
                raise XmlError("error unknown element '%s'"%name)

        # Check the stack, if the stack does not exist then we must be
        # at the root of the xml file, and the tag must be "fileformat".
        # The fileformat tag has no further attributes of interest,
        # so we can exit the function after pushing the tag on the stack.
        if not self.stack:
            if tag != self.tagFile:
                raise XmlError("this is not a fileformat xml file")
            self.pushTag(tag)
            return

        # Now do a number of things, depending on the tag that was last
        # pushed on the stack; this is self.currentTag, and reflects the
        # tag in which <name> is embedded.
        #
        # For each struct, alias, enum, and bitstruct tag, we shall
        # create a class. So assign to C{self.className} the name of that
        # class, C{self.classBase} to the base of that class, and
        # C{self.classDict} to the class dictionary.
        #
        # For a basic tag, C{self.className} is the name of the
        # class and C{self.basicClass} is the corresponding class in
        # C{self.cls}.
        #
        # For a version tag, C{self.versionString} describes the version as a
        # string.
        if self.currentTag == self.tagStruct:
            self.pushTag(tag)
            # struct -> attribute
            if tag == self.tagAttribute:
                # add attribute to class dictionary
                self.classDict["_attrs"].append(
                    StructAttribute(self.cls, attrs))
            # struct -> version
            elif tag == self.tagVersion:
                # set the version string
                self.versionString = str(attrs["num"])
                self.cls.versions[self.versionString] = self.cls.versionNumber(
                    self.versionString)
                # (classDict["_games"] is updated when reading the characters)
            else:
                raise XmlError(
                    "only add and version tags allowed in struct declaration")
        elif self.currentTag == self.tagFile:
            self.pushTag(tag)

            # fileformat -> struct
            if tag == self.tagStruct:
                self.className = attrs["name"]
                # struct types can be organized in a hierarchy
                # if inherit attribute is defined, then look for corresponding
                # base block
                class_basename = attrs.get("inherit")
                if class_basename:
                    # if that base struct has not yet been assigned to a
                    # class, then we have a problem
                    try:
                        self.classBase = getattr(self.cls, class_basename)
                    except KeyError:
                        raise XmlError(
                            "typo, or forward declaration of struct %s"
                            %class_basename)
                else:
                    self.classBase = StructBase
                # istemplate attribute is optional
                # if not set, then the struct is not a template
                # set attributes (see class StructBase)
                self.classDict = {
                    "_isTemplate": attrs.get("istemplate") == "1",
                    "_attrs": [],
                    "_games": {},
                    "__doc__": ""}

            # fileformat -> basic
            elif tag == self.tagBasic:
                self.className = attrs["name"]
                # Each basic type corresponds to a type defined in C{self.cls}.
                # The link between basic types and C{self.cls} types is done
                # via the name of the class.
                self.basicClass = getattr(self.cls, self.className)
                # check the class variables
                is_template = (attrs.get("istemplate") == "1")
                if self.basicClass._isTemplate != is_template:
                    raise XmlError(
                        'class %s should have _isTemplate = %s'
                        %(self.className,is_template))

            # fileformat -> enum
            elif tag == self.tagEnum:
                self.classBase = EnumBase
                self.className = attrs["name"]
                try:
                    numbytes = int(attrs["numbytes"])
                except KeyError:
                    # niftools format uses a storage
                    # get number of bytes from that
                    typename = attrs["storage"]
                    try:
                        typ = getattr(self.cls, typename)
                    except AttributeError:
                        raise XmlError(
                            "typo, or forward declaration of type %s"%typename)
                    numbytes = typ.getSize()
                self.classDict = {"__doc__": "",
                                  "_numbytes": numbytes,
                                  "_enumkeys": [], "_enumvalues": []}

            # fileformat -> alias
            elif tag == self.tagAlias:
                self.className = attrs["name"]
                typename = attrs["type"]
                try:
                    self.classBase = getattr(self.cls, typename)
                except AttributeError:
                    raise XmlError(
                        "typo, or forward declaration of type %s"%typename)
                self.classDict = {"__doc__": ""}

            # fileformat -> bitstruct
            # this works like an alias for now, will add special
            # BitStruct base class later
            elif tag == self.tagBitStruct:
                self.classBase = BitStructBase
                self.className = attrs["name"]
                self.classDict = {"_attrs": [], "__doc__": "",
                                  "_numbytes": int(attrs["numbytes"])}

            # fileformat -> version
            elif tag == self.tagVersion:
                self.versionString = str(attrs["num"])
                self.cls.versions[self.versionString] = self.cls.versionNumber(
                    self.versionString)
                # (self.cls.games is updated when reading the characters)

            else:
                raise XmlError("""
expected basic, alias, enum, bitstruct, struct, or version,
but got %s instead"""%name)

        elif self.currentTag == self.tagVersion:
            raise XmlError("version tag must not contain any sub tags")

        elif self.currentTag == self.tagAlias:
            raise XmlError("alias tag must not contain any sub tags")

        elif self.currentTag == self.tagEnum:
            self.pushTag(tag)
            if not tag == self.tagOption:
                raise XmlError("only option tags allowed in enum declaration")
            value = attrs["value"]
            try:
                # note: use long rather than int to work around 0xffffffff
                # error in qskope
                value = long(value)
            except ValueError:
                value = long(value, 16)
            self.classDict["_enumkeys"].append(attrs["name"])
            self.classDict["_enumvalues"].append(value)

        elif self.currentTag == self.tagBitStruct:
            self.pushTag(tag)
            if tag == self.tagBits:
                # mandatory parameters
                self.classDict["_attrs"].append(
                    BitStructAttribute(self.cls, attrs))
            else:
                raise XmlError(
                    "only bits tags allowed in struct type declaration")

        else:
            raise XmlError("unhandled tag %s"%name)

    def endElement(self, name):
        """Called at the end of each xml tag.

        Creates classes."""
        if not self.stack:
            raise XmlError("mismatching end element tag for element %s"%name)
        try:
            tag = self.tags[name]
        except KeyError:
            try:
                tag = self.tags_niftools[name]
            except KeyError:
                raise XmlError("error unknown element %s"%name)
        if self.popTag() != tag:
            raise XmlError("mismatching end element tag for element %s"%name)
        elif tag == self.tagAttribute:
            return # improves performance
        elif tag in (self.tagStruct,
                     self.tagEnum,
                     self.tagAlias,
                     self.tagBitStruct):
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
        elif tag == self.tagBasic:
            # link class cls.<className> to self.basicClass
            setattr(self.cls, self.className, self.basicClass)
            # reset variable
            self.basicClass = None
        elif tag == self.tagVersion:
            # reset variable
            self.versionString = None

    def endDocument(self):
        """Called when the xml is completely parsed.

        Searches and adds class customized functions.
        For version tags, adds version to version and game lists."""
        for obj in self.cls.__dict__.values():
            # skip objects that are not generated by the C{type} function
            # or that do not derive from StructBase
            if not (isinstance(obj, TypeType) and issubclass(obj, StructBase)):
                continue
            # fix templates
            for attr in obj._attrs:
                templ = attr.template
                if isinstance(templ, basestring):
                    attr.template = \
                        getattr(self.cls, templ) if templ != "TEMPLATE" \
                        else NoneType
                attrtype = attr.type
                if isinstance(attrtype, basestring):
                    attr.type = getattr(self.cls, attrtype)

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
        """Add the string C{chars} to the docstring.
        For version tags, updates the game version list."""
        if self.currentTag in (self.tagAttribute, self.tagBits):
            self.classDict["_attrs"][-1].doc += str(chars.strip())
        elif self.currentTag in (self.tagStruct, self.tagEnum, self.tagAlias):
            self.classDict["__doc__"] += str(chars.strip())
        elif self.currentTag == self.tagVersion:
            # fileformat -> version
            if self.stack[1] == self.tagFile:
                gamesdict = self.cls.games
            # struct -> version
            elif self.stack[1] == self.tagStruct:
                gamesdict = self.classDict["_games"]
            else:
                raise XmlError("version parsing error at '%s'" % chars)
            # update the gamesdict dictionary
            for gamestr in (str(g.strip()) for g in chars.split(',')):
                if gamestr in gamesdict:
                    gamesdict[gamestr].append(
                        self.cls.versions[self.versionString])
                else:
                    gamesdict[gamestr] = [
                        self.cls.versions[self.versionString]]