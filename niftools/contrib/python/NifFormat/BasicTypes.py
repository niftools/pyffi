from FileFormat.Bases.Basic import BasicBase

class Int(BasicBase):
    _isTemplate = False

    def __init__(self):
        self.setValue(0L)

    def getValue(self):
        return self._x

    def setValue(self, value):
        try:
            self._x = long(value)
        except ValueError:
            try:
                self._x = long(value, 16) # for '0x...' strings
            except:
                raise ValueError("cannot convert value '%s' to integer"%str(val))

class UInt(Int):
    _isTemplate = False

    def setValue(self, value):
        Int.setValue(self, value)
        if self._x < 0:
            raise ValueError("negative UInt (%i)"%self._x)

class Bool(Int):
    _isTemplate = False

    def __init__(self):
        self.setValue(False)

    def setValue(self, value):
        if value:
            self._x = True
        else:
            self._x = False

class Byte(Int):
    _isTemplate = False
    
    def setValue(self, value):
        Int.setValue(self, value)
        if self._x < 0 or self._x > 255:
            raise ValueError('Byte out of range (%i)'%self.getValue())

# TODO
class Char(Int):
    _isTemplate = False
    def __init__(self):
        self.setValue('\x00')

    def setValue(self, value):
        assert(isinstance(value, str))
        assert(len(value) == 1)
        self._x = value

# TODO
class Short(Int):
    _isTemplate = False

    def setValue(self, value):
        Int.setValue(self, value)
        if self._x < -32768 or self._x > 32767:
            raise ValueError('Byte out of range (%i)'%self.getValue())

# TODO
class UShort(UInt):
    _isTemplate = False

    def setValue(self, value):
        Int.setValue(self, value)
        if self._x < 0 or self._x > 65535:
            raise ValueError('UShort out of range (%i)'%self.getValue())

# TODO
class Flags(UShort):
    _isTemplate = False

    def __str__(self):
        return hex(self.getValue())

# TODO
class Float(Int):
    _isTemplate = False
    def __init__(self):
        self.setValue(0.0)

    def setValue(self, value):
        self._x = float(value)

class Ref(BasicBase):
    _isTemplate = True
    def __init__(self, tmpl):
        self._template = tmpl
        self.setValue(None)

    def getValue(self):
        return self._x

    def setValue(self, value):
        if value == None:
            self._x = None
        else:
            #assert(isinstance(value, self._template)) # uncomment when forwards are resolved
            self._x = value

class Ptr(Ref):
    _isTemplate = True

    def __str__(self):
        # avoid infinite recursion
        return '%s instance at 0x%08X'%(self._x.__class__, id(self._x))

class LineString(BasicBase):
    _isTemplate = False
    def __init__(self):
        self.setValue('')

    def getValue(self):
        return self._x

    def setValue(self, value):
        self._x = str(value)

    def __str__(self):
        s = BasicBase.__str__(self)
        if not s: return '<EMPTY STRING>'
        return "'" + s + "'"
