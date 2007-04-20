# This metaclass checks for the presence of an _attrs and __doc__ attribute.
# Used as metaclass of _CompoundBase.
class _MetaCompoundBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('_attrs'):
            raise TypeError(str(cls) + ': missing _attrs attribute')
        if not dct.has_key('_isTemplate'):
            raise TypeError(str(cls) + ': missing _isTemplate attribute')

class CompoundBase(object):
    """Base class from which all file compound types are derived.

    The CompoundBase class implements the basic compound interface:
    it will initialize all attributes using the class interface
    using the _attrs class variable, print them as strings, and so on.
    The class variable _attrs *must* be declared every derived class
    interface, see MetaXmlFileFormat.__init__ for an example.
    """
    
    __metaclass__ = _MetaCompoundBase
    
    _isTemplate = False
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
        for name, typ, default, template, arg, arr1, arr2, cond, ver1, ver2, userver in cls._attrs:
            typ_args = []
            if template:
                typ_args.append(template)
            if default:
                typ_args.append(default)
            setattr(self, name, typ(*typ_args))

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
        for name, typ, default, template, arg, arr1, arr2, cond, ver1, ver2, userver in cls._attrs:
            attr_str_lines = str(getattr(self, name)).splitlines()
            if len(attr_str_lines) > 1:
                s += "* " + str(name) + "\n"
                for attr_str in attr_str_lines:
                    s += "    " + attr_str + '\n'
            else:
                s += "* " + str(name) + " : " + attr_str_lines[0] + "\n"
        return s
