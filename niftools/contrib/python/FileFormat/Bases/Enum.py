# This metaclass checks for the presence of an _attrs and __doc__ attribute.
# Used as metaclass of _EnumBase.
class _MetaEnumBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('__doc__'):
            raise TypeError(str(cls) + ': missing __doc__ attribute')

class _EnumBase(object):
    """Base class from which all enum types are derived.

    The _EnumBase class implements the interface for enum types.
    """
    __metaclass__ = _MetaEnumBase
    # initialize all _attrs attributes
    def __init__(self):
        self._value = None

    # string representation of all _attrs attributes
    def __str__(self):
        return str(self._value)
