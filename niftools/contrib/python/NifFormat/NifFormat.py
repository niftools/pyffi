from FileFormat.XmlFileFormat import MetaXmlFileFormat

from FileFormat.Bases.Basic import BasicBase

class Int(BasicBase):
    _isTemplate = False
    def __init__(self, val = 0L):
        try:
            self._value = long(val)
        except ValueError:
            try:
                self._value = long(val, 16) # for '0x...' strings
            except:
                raise ValueError("cannot convert value '%s' to integer"%str(val))

class UInt(Int):
    _isTemplate = False

class Bool(Int):
    _isTemplate = False

class Byte(UInt):
    _isTemplate = False

class Char(UInt):
    _isTemplate = False
    def __init__(self, val = ' '):
        self._value = str(val)[0]

class Short(Int):
    _isTemplate = False

class UShort(UInt):
    _isTemplate = False

class Float(Int):
    _isTemplate = False
    def __init__(self, val = 0L):
        self._value = float(val)

class Ptr(Int):
    _isTemplate = True
    def __init__(self, tmpl, val = -1L):
        self._T = tmpl
        self._value = int(val)

class Ref(Ptr):
    _isTemplate = True
    def __init__(self, tmpl, val = -1L):
        self._T = tmpl
        self._value = int(val)

class LineString(BasicBase):
    _isTemplate = False
    def __init__(self, s):
        self._value = str(s)

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
    <class 'NifFormat.NifFormat.LineString'>
    """
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'nif.xml'
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
        'Flags' : UShort,
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
        
        parts = name.split()
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname
