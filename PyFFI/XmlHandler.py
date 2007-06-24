# --------------------------------------------------------------------------
# PyFFI.XmlHandler
# Parses file format description in XML format and set up representation of
# the file format in memory, as a bunch of classes.
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
# ***** END LICENSE BLOCK *****
# --------------------------------------------------------------------------

import xml.sax
from types import *
import sys

from Bases.Basic      import BasicBase
from Bases.Struct     import StructBase
from Bases.Expression import Expression

class XmlError(Exception):
    pass

class XmlHandler(xml.sax.handler.ContentHandler):
    tagFile      = 1
    tagVersion   = 2
    tagBasic     = 3
    tagAlias     = 4
    tagEnum      = 5
    tagOption    = 6
    tagBitStruct = 7
    tagStruct    = 8
    tagAttribute = 9

    tags = {
    "fileformat" : tagFile,
    "version" : tagVersion,
    "basic" : tagBasic,
    "alias" : tagAlias,
    "enum" : tagEnum,
    "option" : tagOption,
    "bitstruct" : tagBitStruct,
    "struct" : tagStruct,
    "add" : tagAttribute }

    # for compatibility with niftools
    tags_niftools = {
    "niftoolsxml" : tagFile,
    "compound" : tagStruct,
    "niobject" : tagStruct }

    attrName = 0
    attrType = 1
    attrDefault = 2
    attrTemplate = 3
    attrArg = 4
    attrArr1 = 5
    attrArr2 = 6
    attrCond = 7
    attrVer1 = 8
    attrVer2 = 9
    attrUserver = 10
    attrDoc = 11

    def __init__(self, cls, name, bases, dct):
        """Set up the xml parser.

        Creates a dictionary cls.versions which maps each supported
        version strings onto a version integer. Makes an alias
        self.cls for cls. Initializes a stack self.stack of xml tags.
        Initializes the current tag.
        """
        # save dictionary for future use
        self.dct = dct

        # initialize dictionaries
        # cls.version maps each supported version string to a version number
        cls.versions = {}
        # cls.games maps each supported game to a list of version numbers
        cls.games = {}

        # initialize tag stack
        self.stack = []
        self.currentTag = None # last element of self.stack; storing this reduces overhead

        # cls needs to be accessed in member functions, so make it an instance
        # member variable
        self.cls = cls

        # We also keep an ordered list of all classes that have been created.
        # The xmlStruct list includes all xml generated struct classes,
        # including those that are replaced by a native class in cls (for
        # instance NifFormat.String). The idea is that these lists should
        # contain sufficient info from the xml so they can be used to write other
        # python scripts that would otherwise have to implement their own
        # xml parser. See makehsl.py for an example of usage.
        #
        # (note: no classes are created for basic types, so no list for those)
        self.cls.xmlEnum = []
        self.cls.xmlAlias = []
        self.cls.xmlBitStruct = []
        self.cls.xmlStruct = []

    def pushTag(self, x):
        """Push tag x on the stack and make it the current tag."""
        self.stack.insert(0, x)
        self.currentTag = x

    def popTag(self):
        """Pop the current tag from the stack and return it. Also update
        the current tag."""
        lasttag = self.stack.pop(0)
        try:
            self.currentTag = self.stack[0]
        except IndexError:
            self.currentTag = None
        return lasttag

    def startElement(self, name, attrs):
        """This function is called on the start of an xml element <name>."""

        # get the tag identifier
        try:
            x = self.tags[name]
        except KeyError:
            try:
                x = self.tags_niftools[name]
            except KeyError:
                raise XmlError("error unknown element '" + name + "'")

        # Check the stack, if the stack does not exist then we must be
        # at the root of the xml file, and the tag must be "fileformat".
        # The fileformat tag has no further attributes of interest,
        # so we can exit the function after pushing the tag on the stack.
        if not self.stack:
            if x != self.tagFile:
                raise XmlError("this is not a fileformat xml file")
            self.pushTag(x)
            return
        
        # Now do a number of things, depending on the tag that was last
        # pushed on the stack; this is self.currentTag, and reflects the
        # tag in which <name> is embedded.
        # 
        # For each basic, alias, enum, and struct tag, we need to create a
        # class. So we assign to self.class_name the name of that class,
        # to self.class_base the base of that class, and to self.class_dct
        # the class dictionary which describes all class variables.
        #
        # The class variables depend on the type (see the BasicBase and
        # StructBase classes in FileFormat.Bases).
        if self.currentTag == self.tagStruct:
            self.pushTag(x)
            if x == self.tagAttribute:
                # mandatory parameters
                attrs_name = self.cls.nameAttribute(attrs["name"])
                attrs_type_str = attrs["type"]
                if attrs_type_str != "TEMPLATE":
                    try:
                        attrs_type = getattr(self.cls, attrs_type_str)
                    except AttributeError:
                        raise XmlError("typo, or forward declaration of type " + attrs_type_str)
                else:
                    attrs_type = type(None) # type determined at runtime
                # optional parameters
                attrs_default = attrs.get("default")
                attrs_template_str = attrs.get("template")
                attrs_arg = attrs.get("arg")
                attrs_arr1 = attrs.get("arr1")
                attrs_arr2 = attrs.get("arr2")
                attrs_cond = attrs.get("cond")
                attrs_ver1 = attrs.get("ver1")
                attrs_ver2 = attrs.get("ver2")
                attrs_userver = attrs.get("userver")
                attrs_doc = "" # handled in xml parser's characters function

                # post-processing
                if attrs_default:
                    try:
                        tmp = attrs_type()
                        tmp.setValue(attrs_default)
                        attrs_default = tmp.getValue()
                        del tmp
                    except StandardError:
                        # conversion failed; not a big problem
                        attrs_default = None
                if attrs_arr1:
                    attrs_arr1 = Expression(attrs_arr1, self.cls.nameAttribute)
                if attrs_arr2:
                    attrs_arr2 = Expression(attrs_arr2, self.cls.nameAttribute)
                if attrs_cond:
                    attrs_cond = Expression(attrs_cond, self.cls.nameAttribute)
                if attrs_arg:
                    try:
                        attrs_arg = int(attrs_arg)
                    except ValueError:
                        attrs_arg = self.cls.nameAttribute(attrs_arg)
                if attrs_userver:
                    attrs_userver = int(attrs_userver)
                if attrs_ver1:
                    attrs_ver1 = self.cls.versions[attrs_ver1]
                if attrs_ver2:
                    attrs_ver2 = self.cls.versions[attrs_ver2]

                # add attribute to class dictionary
                self.class_dct["_attrs"].append([
                    attrs_name,
                    attrs_type,
                    attrs_default,
                    attrs_template_str,
                    attrs_arg,
                    attrs_arr1,
                    attrs_arr2,
                    attrs_cond,
                    attrs_ver1,
                    attrs_ver2,
                    attrs_userver,
                    attrs_doc])
            else:
                raise XmlError("only add tags allowed in struct type declaration")
        elif self.currentTag == self.tagFile:
            self.pushTag(x)
            
            # fileformat -> struct
            if x == self.tagStruct:
                self.class_name = attrs["name"]
                # struct types can be organized in a hierarchy
                # if inherit attribute is defined, then look for corresponding
                # base block
                try:
                    class_basename = attrs["inherit"]
                except KeyError:
                    class_basename = None
                if class_basename:
                    # if that base struct has not yet been assigned to a
                    # class, then we have a problem
                    try:
                        self.class_base = getattr(self.cls, class_basename)
                    except KeyError:
                        raise XmlError("typo, or forward declaration of struct " + class_basename)
                else:
                    self.class_base = StructBase
                # istemplate attribute is optional
                # if not set, then the struct is not a template
                try:
                    isTemplate = (attrs["istemplate"] == "1")
                except KeyError:
                    isTemplate = False
                # set attributes (see class StructBase)
                self.class_dct = { "_isTemplate" : isTemplate, "_attrs" : [], "__doc__" : "" }

            # fileformat -> basic
            elif x == self.tagBasic:
                self.class_name = attrs["name"]
                # Each basic type corresponds to a type defined in python, and
                # the link between basic types and python types is stored in
                # self.cls.basicClasses, which is a dictionary mapping
                # basic type names onto BasicBase derived classes
                self.basic_class = getattr(self.cls, self.class_name)
                # check the class variables
                try:
                    istemplate = (attrs["istemplate"] == "1")
                except KeyError:
                    istemplate = False
                if self.basic_class._isTemplate != istemplate:
                    raise XmlError('class %s should have _isTemplate = %s'%(self.class_name,istemplate))

            # fileformat -> enum
            elif x == self.tagEnum:
                self.class_name = attrs["name"]
                try:
                    typename = attrs["type"]
                except KeyError:
                    typename = attrs["storage"] # niftools
                try:
                    self.class_base = getattr(self.cls, typename)
                except AttributeError:
                    raise XmlError("typo, or forward declaration of type " + typename)
                self.class_dct = {"__doc__" : ""}

            # fileformat -> alias
            elif x == self.tagAlias:
                self.class_name = attrs["name"]
                typename = attrs["type"]
                try:
                    self.class_base = getattr(self.cls, typename)
                except AttributeError:
                    raise XmlError("typo, or forward declaration of type " + typename)
                self.class_dct = {"__doc__" : ""}

            # fileformat -> bitstruct
            # TODO: this works like an alias for now, will add special
            #       BitStruct base class later
            elif x == self.tagBitStruct:
                self.class_name = attrs["name"]
                typename = attrs["type"]
                try:
                    self.class_base = getattr(self.cls, typename)
                except AttributeError:
                    raise XmlError("typo, or forward declaration of type " + storagename)
                self.class_dct = {"_attrs" : [], "__doc__" : ""}
                
            # fileformat -> version
            elif x == self.tagVersion:
                self.version_str = str(attrs["num"])
                self.cls.versions[self.version_str] = self.cls.versionNumber(self.version_str)

            else:
                raise XmlError("expected basic, alias, enum, bitstruct, struct, or version, but got " + name + " instead")

        elif self.currentTag == self.tagVersion:
            raise XmlError( "version tag must not contain any sub tags" )

        elif self.currentTag == self.tagAlias:
            raise XmlError( "alias tag must not contain any sub tags" )

        elif self.currentTag == self.tagEnum:
            self.pushTag(x)
            if not x == self.tagOption:
                raise XmlError( "only option tags allowed in enum declaration" )
            value = attrs["value"]
            try:
                value = int(value)
            except ValueError:
                value = int(value, 16)
            self.class_dct[attrs["name"]] = value

        elif self.currentTag == self.tagBitStruct:
            self.pushTag(x)
            if x == self.tagAttribute:
                # mandatory parameters
                attrs_name = self.cls.nameAttribute(attrs["name"])
                attrs_numbits = int(attrs["numbits"])
                # optional parameters
                attrs_default = attrs.get("default")
                attrs_doc = "" # handled in xml parser's characters function

                # add attribute to class dictionary
                self.class_dct["_attrs"].append([
                    attrs_name,
                    attrs_numbits,
                    attrs_default,
                    attrs_doc])
            else:
                raise XmlError("only add tags allowed in struct type declaration")
            
        else:
            raise XmlError( "unhandled tag " + name);
    
    def endElement(self, name):
        if not self.stack:
            raise XmlError( "mismatching end element tag for element " + name )
        try:
            x = self.tags[name]
        except KeyError:
            try:
                x = self.tags_niftools[name]
            except KeyError:
                raise XmlError("error unknown element '" + name + "'")
        if self.popTag() != x:
            raise XmlError( "mismatching end element tag for element " + name )
        #x = self.popTag()
        if x == self.tagAttribute:
            return # improves performance
        if x in [ self.tagStruct, self.tagEnum, self.tagAlias, self.tagBitStruct ]:
            # create class cls.<class_name> (if it has not been implemented internally)
            class_type = type(str(self.class_name), (self.class_base,), self.class_dct)
            if not self.cls.__dict__.has_key(self.class_name):
                setattr(self.cls, self.class_name, class_type)
            if x == self.tagStruct:
                self.cls.xmlStruct.append(class_type)
            elif x == self.tagEnum:
                self.cls.xmlEnum.append(class_type)
            elif x == self.tagAlias:
                self.cls.xmlAlias.append(class_type)
            elif x == self.tagBitStruct:
                self.cls.xmlBitStruct.append(class_type)
        elif x == self.tagBasic:
            # link class cls.<class_name> to self.basic_class
            setattr(self.cls, self.class_name, self.basic_class)

    def endDocument(self):
        for obj in self.cls.__dict__.values():
            try:
                if not issubclass(obj, StructBase): continue
            except:
                continue
            # forward declarations
            for a in obj._attrs:
                templ = a[self.attrTemplate]
                if isinstance(templ, basestring):
                    if templ != "TEMPLATE":
                        a[self.attrTemplate] = getattr(self.cls, templ)
                    else:
                        a[self.attrTemplate] = type(None)

            # add custom functions to interface
            # first find the module
            sys.path.append(self.dct['clsFilePath'])
            try:
                # TODO find better solution to import the custom object module
                mod = __import__(obj.__name__, globals(),  locals(), [])
            except ImportError:
                continue
            finally:
                sys.path.pop()
            props = {}
            # set object's cls argument to give it access to other objects
            # defined in self.cls
            obj.cls = self.cls
            # iterate over all objects defined in the module
            for x, xfunc in mod.__dict__.items():
                # skip if it is not a function
                if not isinstance(xfunc, FunctionType): continue
                # register property getter
                if x[:5] == "_get_":
                    xname = x[5:]
                    if props.has_key(xname):
                        props[xname][0] = xfunc
                    else:
                        props[xname] = [xfunc, None, None, None]
                # register property setter
                elif x[:5] == "_set_":
                    xname = x[5:]
                    if props.has_key(xname):
                        props[xname][1] = xfunc
                    else:
                        props[xname] = [None, xfunc, None, None]
                # set regular method
                else:
                    setattr(obj, x, xfunc)
            # set all properties
            for x, arglist in props.items():
                setattr(obj, x, property(*arglist))

    def characters(self, s):
        if self.currentTag == self.tagAttribute:
            self.class_dct["_attrs"][-1][self.attrDoc] += str(s.strip())
        elif self.currentTag in [self.tagStruct, self.tagEnum, self.tagAlias]:
            self.class_dct["__doc__"] += str(s.strip())
        elif self.currentTag == self.tagVersion:
            for gamestr in [str(g.strip()) for g in s.split(',')]:
                if self.cls.games.has_key(gamestr):
                    self.cls.games[gamestr].append(self.cls.versions[self.version_str])
                else:
                    self.cls.games[gamestr] = [self.cls.versions[self.version_str]]

##    {
##        switch ( current() )
##        {
##            case tagVersion:
##                break;
##            case tagStruct:
##                if ( blk )
##                    blk->text += s.trimmed();
##                else
##                    typTxt += s.trimmed();
##                break;
##            case tagAttribute:
##                data.setText( data.text() + s.trimmed() );
##                break;
##            case tagBasic:
##            case tagEnum:
##                typTxt += s.trimmed();
##                break;
##            case tagOption:
##                optTxt += s.trimmed();
##                break;
##            default:
##                break;
##        }
##        return true;
##    }
