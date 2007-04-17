# This metaclass checks for the presence of an _attrs and __doc__ attribute.
# Used as metaclass of _BlockBase.
class _MetaBlockBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('_attrs'):
            raise TypeError(str(cls) + ': missing _attrs attribute')
        if not dct.has_key('__doc__'):
            raise TypeError(str(cls) + ': missing __doc__ attribute')

class _BlockBase(object):
    """Base class from which all file block types are derived.

    The _BlockBase class implements the basic block interface:
    it will initialize all attributes using the class interface
    using the _attrs class variable, print them as strings, and so on.
    The class variable _attrs *must* be declared every derived class
    interface, see MetaXmlFileFormat.__init__ for an example.
    """
    __metaclass__ = _MetaBlockBase
    _attrs = []
    # initialize all _attrs attributes
    def __init__(self):
        self._initAttributes(self.__class__)

    # initialize all attributes in cls._attrs
    # (plus all bases of cls)
    def _initAttributes(self, cls):
        # are we at the end of class recursion?
        if cls == object: return
        # initialize attributes of base classes of cls
        for base in cls.__bases__:
            self._initAttributes(base)
        # initialize attributes defined in cls._attrs
        for name, default in cls._attrs:
            setattr(self, name, default)

    # string representation of all _attrs attributes
    def __str__(self):
        return self._strAttributes(self.__class__)

    # string of all attributes in cls._attrs
    # (plus all bases of cls)
    def _strAttributes(self, cls):
        s = ''
        # are we at the end of class recursion?
        if cls == object: return s
        # string of attributes of base classes of cls
        for base in cls.__bases__:
            s += self._strAttributes(base)
        # string of attributes defined in cls._attrs
        for name, default in cls._attrs:
            s += str(name) + ' : ' + str(getattr(self, name)) + '\n'
        return s
