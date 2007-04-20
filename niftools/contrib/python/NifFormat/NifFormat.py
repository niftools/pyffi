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
        v = version_str.split('.')
        num = 0
        shift = 24
        for x in v:
            num += int(x) << shift
            shift -= 8
        return num

    @staticmethod
    def nameAttribute(name):
        parts = name.split()
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname
