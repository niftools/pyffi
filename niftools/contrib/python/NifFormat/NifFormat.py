from FileFormat.XmlFileFormat import MetaXmlFileFormat
from BasicTypes import *

class NifFormat(object):
    """Stores all information about the nif file format.
    
    >>> for vnum in sorted(NifFormat.versions.values()): print '0x%08X'%vnum
    0x03010000
    0x0303000D
    0x04000000
    0x04000002
    0x0401000C
    0x04020002
    0x04020100
    0x04020200
    0x0A000100
    0x0A000102
    0x0A010000
    0x0A01006A
    0x0A020000
    0x14000004
    0x14000005
    >>> print NifFormat.HeaderString
    <class 'NifFormat.BasicTypes.LineString'>
    """
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'nif.xml'
    xmlFilePath = [ '.', '../../docsys' ]
    basicClasses = {
        'int'    : Int,
        'uint'   : UInt,
        'bool'   : Bool,
        'byte'   : Byte,
        'char'   : Char,
        'short'  : Short,
        'ushort' : UShort,
        'float'  : Float,
        'Ptr'    : Ptr,
        'Ref'    : Ref,
        'BlockTypeIndex' : UShort,
        'StringOffset' : UInt,
        'FileVersion' : UInt,
        'Flags' : Flags,
        'HeaderString' : LineString,
        'LineString' : LineString }

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.

        >>> hex(NifFormat.versionNumber('3.14.15.29'))
        '0x30e0f1d'
        >>> hex(NifFormat.versionNumber('1.2'))
        '0x1020000'
        """
        
        v = version_str.split('.')
        num = 0
        shift = 24
        for x in v:
            num += int(x) << shift
            shift -= 8
        return num

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable by python.

        >>> NifFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """
        
        parts = str(name).split() # str(name) converts name to string in case name is a unicode string
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname
