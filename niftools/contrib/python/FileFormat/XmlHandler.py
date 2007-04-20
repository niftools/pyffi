# --------------------------------------------------------------------------
# FileFormat.XmlHandler
# Parses file format description in XML format and set up representation of
# the file format in memory, as a bunch of classes.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
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

import xml.sax

from Bases.Basic    import BasicBase
from Bases.Compound import CompoundBase
from Bases.Block    import BlockBase

class XmlError(Exception):
    pass

class XmlHandler(xml.sax.handler.ContentHandler):
    tagNone      = 0
    tagFile      = 1
    tagVersion   = 2
    tagCompound  = 3
    tagBlock     = 4
    tagAttribute = 5
    tagBasic     = 6
    tagEnum      = 7
    tagOption    = 8
    tags = {
    "niftoolsxml" : tagFile,
    "version" : tagVersion,
    "compound" : tagCompound,
    "niobject" : tagBlock,
    "add" : tagAttribute,
    "basic" : tagBasic,
    "enum" : tagEnum,
    "option" : tagOption }

    def __init__(self, cls, name, bases, dct):
        """Set up the xml parser.

        Creates a dictionary cls.versions which maps each supported
        version strings onto a version integer. Makes an alias
        self.cls for cls. Initializes a stack self.stack of xml tags.
        Initializes the current tag.
        """
        
        # initialize dictionary of versions
        # this will map each supported version string to a version number
        cls.versions = {}

        # initialize tag stack
        self.stack = []
        self.currentTag = None # last element of self.stack; storing this reduces overhead
        # cls needs to be accessed in member functions, so make it an instance
        # member variable
        self.cls = cls
    
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
            raise XmlError("error unknown element '" + name + "'")

        # Check the stack, if the stack does not exist then we must be
        # at the root of the xml file, and the tag must be "niftoolsxml".
        # The niftoolsxml tag has no further attributes of interest,
        # so we can exit the function after pushing the tag on the stack.
        if not self.stack:
            if x != self.tagFile:
                raise XmlError("this is not a niftoolsxml file")
            self.pushTag(x)
            return
        
        # Now do a number of things, depending on the tag that was last
        # pushed on the stack; this is self.currentTag, and reflects the
        # tag in which <name> is embedded.
        # 
        # For each basic, enum, compound, and block tag, we need to create a
        # class. So we assign to self.class_name the name of that class,
        # to self.class_base the base of that class, and to self.class_dct
        # the class dictionary which describes all class variables.
        #
        # The class variables depend on the type (see the BasicBase,
        # CompoundBase, and BlockBase classes in FileFormat.Bases).
        if self.currentTag == self.tagFile:
            self.pushTag(x)
            
            # niftoolsxml -> compound
            if x == self.tagCompound:
                self.class_name = attrs["name"]
                # compound types are all derived from the same base type
                self.class_base = CompoundBase
                # istemplate attribute is optional
                # if not set, then the compound is not a template
                try:
                    isTemplate = (attrs["istemplate"] == "1")
                except KeyError:
                    isTemplate = False
                # set attributes (see class CompoundBase)
                self.class_dct = { "_isTemplate" : isTemplate, "_attrs" : [] }

            # niftoolsxml -> block
            elif x == self.tagBlock:
                self.class_name = attrs["name"]
                # block types are organized in a hierarchy
                # if inherit attribute is defined, then look for corresponding
                # base block
                try:
                    class_basename = attrs["inherit"]
                except KeyError:
                    class_basename = None
                if class_basename:
                    # if that base block has not yet been assigned to a
                    # class, then we have a problem
                    try:
                        self.class_base = getattr(self.cls, class_basename)
                    except KeyError:
                        raise XmlError("typo, or forward declaration of block " + class_basename)
                else:
                    self.class_base = BlockBase
                # set attributes (see class BlockBase)
                self.class_dct = { "_isTemplate" : False, "_isAbstract" : (attrs["abstract"] == "1"), "_attrs" : [] }

            # niftoolsxml -> basic
            elif x == self.tagBasic:
                self.class_name = attrs["name"]
                # Each basic type corresponds to a type defined in python, and
                # the link between basic types and python types is stored in
                # self.cls.basicClasses, which is a dictionary mapping
                # basic type names onto BasicBase derived classes
                self.basic_class = self.cls.basicClasses[self.class_name]
                # check the class variables
                # (ignore iscount)
                #iscount = (attrs["count"] == "1")
                try:
                    istemplate = (attrs["istemplate"] == "1")
                except KeyError:
                    istemplate = False
                if self.basic_class.__dict__['_isTemplate'] != istemplate:
                    raise XmlError('class %s should have _isTemplate = %s'%(self.class_name,istemplate))

            # niftoolsxml -> enum
            elif x == self.tagEnum:
                self.class_name = attrs["name"]
                storagename = attrs["storage"]
                try:
                    storage = getattr(self.cls, storagename)
                except AttributeError:
                    raise XmlError("typo, or forward declaration of type " + storagename)
                self.class_base = storage
                self.class_dct  = { "_isTemplate" : False }

            # niftoolsxml -> version
            elif x == self.tagVersion:
                version_str = str(attrs["num"])
                self.cls.versions[version_str] = self.cls.versionNumber(version_str)

            else:
                raise XmlError("expected basic, enum, compound, niobject, or version, but got " + name + " instead")

        elif self.currentTag == self.tagVersion:
            raise XmlError( "version tag must not contain any sub tags" )

        elif self.currentTag in [ self.tagCompound, self.tagBlock ]:
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
                    attrs_type = None # type determined at runtime, self.T
                # optional parameters
                attrs_default  = None
                attrs_template = None
                attrs_arg      = None
                attrs_arr1     = None
                attrs_arr2     = None
                attrs_cond     = None
                attrs_ver1     = None
                attrs_ver2     = None
                attrs_userver  = None
                if attrs.has_key("default"):
                    try:
                        attrs_default = attrs_type._pythontype(attrs["default"])
                    except:
                        # conversion failed; not a big problem
                        attrs_default = None
                if attrs.has_key("template"):
                    attrs_template = attrs["template"]
                if attrs.has_key("arg"):
                    attrs_arg = attrs["arg"]
                if attrs.has_key("arr1"):
                    attrs_arr1 = attrs["arr1"]
                if attrs.has_key("arr2"):
                    attrs_arr2 = attrs["arr2"]
                if attrs.has_key("cond"):
                    attrs_cond = attrs["cond"]
                if attrs.has_key("ver1"):
                    attrs_ver1 = self.cls.versions[attrs["ver1"]]
                if attrs.has_key("ver2"):
                    attrs_ver2 = self.cls.versions[attrs["ver2"]]
                if attrs.has_key("userver"):
                    attrs_userver = int(attrs["userver"])

                self.class_dct["_attrs"].append( (
                    attrs_name,
                    attrs_type,
                    attrs_default,
                    attrs_template,
                    attrs_arg,
                    attrs_arr1,
                    attrs_arr2,
                    attrs_cond,
                    attrs_ver1,
                    attrs_ver2,
                    attrs_userver ) )
            else:
                raise XmlError("only add tags allowed in block and compound type declaration")
        elif self.currentTag == self.tagEnum:
            self.pushTag(x)
            if not x == self.tagOption:
                raise XmlError( "only option tags allowed in enum declaration" )
            self.class_dct[attrs["name"]] = int(attrs["value"])
        else:
            raise XmlError( "unhandled tag " + name);
    
    def endElement(self, name):
        if not self.stack:
            raise XmlError( "mismatching end element tag for element " + name )
        x = self.tags[name];
        if self.popTag() != x:
            raise XmlError( "mismatching end element tag for element " + name )
        if x in [ self.tagBlock, self.tagCompound, self.tagEnum ]:
            # create class cls.<class_name>
            setattr(self.cls, self.class_name, type(str(self.class_name), (self.class_base,), self.class_dct))
        elif x in [ self.tagBasic ]:
            # link class cls.<class_name> to self.basic_class
            setattr(self.cls, self.class_name, self.basic_class)

##    bool checkType( const NifData & data )
##    {
##        return NifModel::compounds.contains( data.type() ) || NifValue::type( data.type() ) != NifValue::tNone || data.type() == "TEMPLATE";
##    }
##    
##    bool checkTemp( const NifData & data )
##    {
##        return data.temp().isEmpty() || NifValue::type( data.temp() ) != NifValue::tNone || data.temp() == "TEMPLATE" || NifModel::blocks.contains( data.temp() );
##    }
##    
##    bool endDocument()
##    {   // make a rough check of the maps
##        foreach ( QString key, NifModel::compounds.keys() )
##        {
##            NifBlock * c = NifModel::compounds.value( key );
##            foreach ( NifData data, c->types )
##            {
##                if ( ! checkType( data ) )
##                    raise XmlError( "compound type " + key + " referes to unknown type " + data.type() );
##                if ( ! checkTemp( data ) )
##                    raise XmlError( "compound type " + key + " referes to unknown template type " + data.temp() );
##                if ( data.type() == key )
##                    raise XmlError( "compound type " + key + " contains itself" );
##            }
##        }
##        
##        foreach ( QString key, NifModel::blocks.keys() )
##        {
##            NifBlock * blk = NifModel::blocks.value( key );
##            if ( ! blk->ancestor.isEmpty() && ! NifModel::blocks.contains( blk->ancestor ) )
##                raise XmlError( "niobject " + key + " inherits unknown ancestor " + blk->ancestor );
##            if ( blk->ancestor == key )
##                raise XmlError( "niobject " + key + " inherits itself" );
##            foreach ( NifData data, blk->types )
##            {
##                if ( ! checkType( data ) )
##                    raise XmlError( "niobject " + key + " refraise XmlErrores to unknown type " + data.type() );
##                if ( ! checkTemp( data ) )
##                    raise XmlError( "niobject " + key + " referes to unknown template type " + data.temp() );
##            }
##        }
##        
##        return true;
##    }
