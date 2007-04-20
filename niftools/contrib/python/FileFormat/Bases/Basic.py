# This metaclass checks for the presence of an _attrs and __doc__ attribute.
# Used as metaclass of BasicBase.
class _MetaBasicBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('_isTemplate'):
            raise TypeError(str(cls) + ': missing _isTemplate attribute')

class BasicBase(object):
    """Base class from which all basic types are derived.
    
    The BasicBase class implements the interface for basic types.
    All basic types have to be derived from this class, by hand.
    """
    
    __metaclass__ = _MetaBasicBase
    _isTemplate = False
    
    # initialize _value attribute
    def __init__(self):
        self._value = None

    # string representation of _value
    def __str__(self):
        return str(self._value)

    def read(self, f):
        raise NotImplementedError

    def write(self, f):
        raise NotImplementedError
