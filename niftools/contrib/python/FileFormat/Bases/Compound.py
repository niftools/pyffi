from Basic import BasicBase

# This metaclass checks for the presence of an _attrs and _isTemplate attribute.
# Used as metaclass of _CompoundBase.
class _MetaCompoundBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('_attrs'):
            raise TypeError(str(cls) + ': missing _attrs attribute')
        if not dct.has_key('_isTemplate'):
            raise TypeError(str(cls) + ': missing _isTemplate attribute')
        if not dct.has_key('_isAbstract'):
            raise TypeError(str(cls) + ': missing _isAbstract attribute')
        for attrname in dct['_attrs']:
            if not dct.has_key('_' + attrname + '_info_'):
                raise TypeError(str(cls) + ': missing _' + attrname + '_info_ attribute')
        # TODO automatic attribute properties

class CompoundBase(object):
    """Base class from which all file compound types are derived.

    The CompoundBase class implements the basic compound interface:
    it will initialize all attributes using the class interface
    using the _attrs class variable, print them as strings, and so on.
    The class variable _attrs must be declared every derived class
    interface.

    For each string <name> in the _attrs list, there must be a class
    variable _<name>_info_. Upon instanciation, the compound will create an
    instance variable _<name>_value_. The _<name>_info_ class variable
    stores the information about the attribute as stored for instance
    in the xml file, and the _<name>_value_ instance variable stores the
    actual attribute instance. Access to these instances is
    implemented via the getAttribute and setAttribute functions below.

    Direct access to the attributes can be implemented using a <name>
    property using these get and set functions, as demonstrated below

    See the FileFormat.XmlHandler class for a more advanced example.

    (TODO handle property statements in metaclass and remove them below)

    >>> from Basic import BasicBase
    >>> class UInt(BasicBase):
    ...     _isTemplate = False
    ...     def __init__(self):
    ...         self.__value = 0
    ...     def getValue(self):
    ...         return self.__value
    ...     def setValue(self, value):
    ...         self.__value = int(value)
    >>> class X(CompoundBase):
    ...     _isTemplate = False
    ...     _isAbstract = True
    ...     _attrs = ['a', 'b']
    ...     _a_info_ = (UInt, None, None, None, None, None, None, None, None, None)
    ...     _b_info_ = (UInt, None, None, None, None, None, None, None, None, None)
    ...     a = property(lambda self: self.getAttribute('a'), lambda self, value: self.setAttribute('a', value))
    ...     b = property(lambda self: self.getAttribute('b'), lambda self, value: self.setAttribute('b', value))
    >>> class Y(X):
    ...     _isTemplate = False
    ...     _isAbstract = True
    ...     _attrs = ['c', 'd']
    ...     _c_info_ = (UInt, None, None, None, None, None, None, None, None, None)
    ...     _d_info_ = (X, None, None, None, None, None, None, None, None, None)
    ...     c = property(lambda self: self.getAttribute('c'), lambda self, value: self.setAttribute('c', value))
    ...     d = property(lambda self: self.getAttribute('d'), lambda self, value: self.setAttribute('d', value))
    >>> y = Y()
    >>> print y.getAttributeNames()
    ['a', 'b', 'c', 'd']
    >>> y.a = 1
    >>> y.b = 2
    >>> y.c = 3
    >>> y.d = X()
    >>> y.d.a = 4
    >>> y.d.b = 5
    >>> print y # doctest:+ELLIPSIS
    <class 'FileFormat.Bases.Compound.Y'> instance at 0x...
    * a : 1
    * b : 2
    * c : 3
    * d :
        <class 'FileFormat.Bases.Compound.X'> instance at 0x...
        * a : 4
        * b : 5
    <BLANKLINE>
    """
    
    __metaclass__ = _MetaCompoundBase
    
    _isTemplate = False
    _isAbstract = True
    _attrs = []
    
    # initialize all attributes
    def __init__(self, template = type(None)):
        for name in self.getAttributeNames():
            typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver = getattr(self, "_" + name + "_info_")
            if typ == type(None):
                assert(template != type(None))
                assert(self._isTemplate)
                typ = template
            else:
                assert(not self._isTemplate)
            typ_args = []
            if tmpl != None:
                typ_args.append(tmpl)
            #if default:
            #    typ_args.append(default)
            if not arr1:
                attr_instance = typ(*typ_args)
            elif not arr2:
                attr_instance = [] # TODO implement Array class
            else:
                attr_instance = [[]] # TODO implement Array class
            setattr(self, "_" + name + "_value_", attr_instance)

    # string of all attributes
    def __str__(self):
        s = '%s instance at 0x%08X\n'%(self.__class__, id(self))
        for name in self.getAttributeNames():
            typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver = getattr(self, "_" + name + "_info_")
            attr_str_lines = str(getattr(self, "_" + name + "_value_")).splitlines()
            if len(attr_str_lines) > 1:
                s += '* ' + str(name) + ' :\n'
                for attr_str in attr_str_lines:
                    s += '    ' + attr_str + '\n'
            else:
                s += '* ' + str(name) + ' : ' + attr_str_lines[0] + '\n'
        return s

    @classmethod
    def getAttributeNames(cls):
        # string of attributes of base classes of cls
        attrs = []
        for base in cls.__bases__:
            if issubclass(base, CompoundBase):
                attrs.extend(base.getAttributeNames())
        for name in cls._attrs:
            attrs.append(name)
        return attrs

    def getAttribute(self, name):
        typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver = getattr(self, "_" + name + "_info_")
        if issubclass(typ, BasicBase):
            return getattr(self, "_" + name + "_value_").getValue()
        else:
            return getattr(self, "_" + name + "_value_")

    def setAttribute(self, name, value):
        typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver = getattr(self, "_" + name + "_info_")
        if issubclass(typ, BasicBase):
            getattr(self, "_" + name + "_value_").setValue(value)
        else:
            setattr(self, "_" + name + "_value_", value)
