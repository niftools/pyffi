# --------------------------------------------------------------------------
# Nif.XmlHandler
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

from string import Template
import xml.sax

from Element.Basic    import _BasicBase
from Element.Enum     import _EnumBase
from Element.Compound import _CompoundBase
from Element.Block    import _BlockBase

class XmlError(Exception):
    pass

class XmlHandler(xml.sax.handler.ContentHandler):
    tagNone     = 0
    tagFile     = 1
    tagVersion  = 2
    tagCompound = 3
    tagBlock    = 4
    tagAttribute   = 5
    tagBasic    = 6
    tagEnum     = 7
    tagOption   = 8
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
        # initialize tag stack
        self.stack = []
        # initialize dictionary of versions
        self.cls.versions = {}
        # cls needs to be accessed in member functions, so make it an instance
        # member variable
        self.cls = cls
    
    def currentTag(self):
        return self.stack[len(self.stack)-1]

    def pushTag(self, x):
        self.stack.append(x)

    def popTag(self):
        return self.stack.pop()
    
    def startElement(self, name, attrs):
        if len(self.stack) >= 8:
            raise XmlError("error maximum nesting level exceeded")

        try:
            x = self.tags[name]
        except KeyError:
            raise XmlError("error unknown element '" + name + "'")
        
        if not self.stack:
            if x != self.tagFile:
                raise XmlError("this is not a niftoolsxml file")
            self.pushTag(x)
            return
        
        current_tag = self.currentTag()
        if current_tag == self.tagFile:
            self.pushTag(x)
            if x == self.tagCompound:
                self.class_name = attrs["name"]
                self.class_base = _CompoundBase
                try:
                    self.compound_isTemplate = (attrs["istemplate"] == "1")
                except KeyError:
                    self.compound_isTemplate = False

            elif x == self.tagBlock:
                self.class_name = attrs["name"]
                try:
                    class_basename = attrs["inherit"]
                except KeyError:
                    class_basename = None
                if class_basename:
                    try:
                        self.class_base = getattr(self.cls, class_basename)
                    except KeyError:
                        raise XmlError("forward declaration of block " + class_basename)
                else:
                    self.class_base = _BlockBase
                self.block_isAbstract = (attrs["abstract"] == "1")

            elif x == self.tagBasic:
                self.class_name = attrs["name"]
                self.class_base = _BasicBase
                self.basic_isCount = (attrs["count"] == "1")

            elif x == self.tagEnum:
                self.class_name = attrs["name"]
                self.class_base = _EnumBase
                enum_storagename = attrs["storage"]
                try:
                    self.enum_storage = getattr(self.cls, enum_storagename)
                except KeyError:
                    raise XmlError("forward declaration of block" + enum_storagename)

            elif x == self.tagVersion:
                version_str = attrs["num"]
                self.cls.version[version_str] = self.cls.versionNumber(version_str)

            else:
                raise XmlError("expected basic, enum, compound, niobject, or version, but got " + name + " instead")

        elif current_tag == self.tagVersion:
            raise XmlError( "version tag must not contain any sub tags" )

        elif current_tag in [ self.tagCompound, self.tagBlock ]:
            self.pushTag(x)
            if x == self.tagAttribute:
                if not self.__dict__.has_key('block_attrs'):
                    self.block_attrs = []
                self.block_attrs.append( (
                    attrs["name"],
                    getattr(self.cls, attrs["type"] ),
                    attrs["default"],
                    attrs["template"],
                    attrs["arg"],
                    attrs["arr1"],
                    attrs["arr2"],
                    attrs["cond"],
                    self.cls.versions[attr["ver1"]],
                    self.cls.versions[attr["ver2"]],
                    int(attrs["userver"]) ) )
            else:
                raise XmlError("only add tags allowed in block and compound type declaration")
        elif current_tag == self.tagEnum:
            self.pushTag(x)
            if not x == self.tagOption:
                raise XmlError( "only option tags allowed in enum declaration" )
            if not self.__dict__.has_key('enum_options'):
                self.enum_options = []
            self.enum_options.append( (attrs["name"], int(attrs["value"]) ) )
        else:
            raise XmlError( "unhandled tag " + name);
    
    def endElement(self, name):
        if not self.stack:
            raise XmlError( "mismatching end element tag for element " + name )
        x = self.tags[name];
        if self.popTag() != x:
            raise XmlError( "mismatching end element tag for element " + name )
        if x in [ self.tagBlock, self.tagCompound ]:
            if not blk._name:
                del blk
                raise XmlError( "invalid " + name + " declaration: name is empty" );
            self.fileFormat.registerType(blk);
            del blk
        elif x == self.tagAttribute:
            blk.addAttribute(data);
        elif x == self.tagOption:
            self._enumType.addOption(self._enumOption)
            del self._enumOption
        elif x == self.tagBasic:
            self.fileFormat.registerType(self._basicType)
            del self._basicType
        elif x == self.tagEnum:
            self.fileFormat.registerType(self._enumType)
            del self._enumType
        elif x == self.tagVersion:
            self.fileFormat.registerVersion(self._version)
            del self._version

##    bool characters( const QString & s )
##    {
##        switch ( current() )
##        {
##            case tagVersion:
##                break;
##            case tagCompound:
##            case tagBlock:
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
##    
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
