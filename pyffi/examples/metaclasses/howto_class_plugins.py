"""This script is a conceptual demonstration of how class plugins can be
implemented using metaclasses."""

class AClass(object):
    """Base class."""
    pass

class BClass:
    """Another class."""
    def __init__(self):
        """Initialize."""
        self.x = AClass()

# now let's add a function to AClass
# for some reason we do not wish to change the AClass definition directly
# (for example it resides in a module written by someone else)
# but we do wish BClass to profit from an updated version of AClass

def raise_plugin_error(self):
    """Raised if plugin class tries to instanciate."""
    raise RuntimeError("plugin class should not be instanciated")

class MetaClassPlugin(type):
    """This metaclass will copy all attributes of the class to the base class,
    effectively modifying the base class."""
    def __init__(cls, name, bases, dct):
        assert(len(bases) == 1)
        base = bases[0]
        for key, value in dct.iteritems():
            # skip built-in methods
            if key[:2] == "__":
                continue
            # add anything else to the base class
            setattr(base, key, value)

        # make instanciation raise an error
        setattr(cls, "__init__", raise_plugin_error)

# with this metaclass, we can add functions to AClass without explicit
# setattr calls

class AClassPlugin(AClass):
    """Plugin for AClass."""
    __metaclass__ = MetaClassPlugin
    def an_extra_function(self):
        """A function providing extra functionality to AClass."""
        print "I'm doing something extra."

x = BClass()
x.x.an_extra_function()

y = AClassPlugin() # runtime error!

