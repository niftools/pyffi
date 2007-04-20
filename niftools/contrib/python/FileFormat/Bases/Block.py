from Compound import CompoundBase

# This metaclass checks for the presence of required attributes.
# Used as metaclass of BlockBase.
class _MetaBlockBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('_isAbstract'):
            raise TypeError(str(cls) + ': missing _isAbstract attribute')

class BlockBase(CompoundBase):
    """Base class from which all file block types are derived.

    The BlockBase class implements the basic block interface:
    it will initialize all attributes using the class interface
    using the _attrs class variable, print them as strings, and so on.
    The class variable _attrs *must* be declared every derived class
    interface, see MetaXmlFileFormat.__init__ for an example.
    """

    _isTemplate = False
    _isAbstract = False
    _attrs = []

    def __init__(self):
        CompoundBase.__init__(self)

    def __str__(self):
        print self.__class__
        return CompoundBase.__str__(self)
