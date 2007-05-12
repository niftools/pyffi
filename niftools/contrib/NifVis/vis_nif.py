from NifFormat.NifFormat import NifFormat

TypeRegistry = {}
BlockRegistry = []

#
# A simple custom exception class.
#
class NIFImportError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



def LoadNif( filename ):
    try: # catch NIFImportErrors
        # read the NIF file
        print "Reading Nif: %s" % filename
        f = open( filename, "rb" )
        version, user_version = NifFormat.getVersion( f )
        if version >= 0:
                print "( version 0x%08X )" % version
                root_blocks = NifFormat.read( version, user_version, f, verbose = 0 )
                for block in root_blocks:
                    AddBlock( block )
        elif version == -1:
            raise NIFImportError( "Unsupported NIF version." )
        else:
            raise NIFImportError( "Not a NIF file." )
    
    except NIFImportError, e: # in that case, we raise a menu instead of an exception
        print 'NIFImportError: ' + e.value
        return



def AddBlock( block ):
    if not block: return
    
    if not TypeRegistry.has_key( type( block ).__name__ ):
        TypeRegistry[type( block ).__name__] = []
    
    TypeRegistry[type( block ).__name__].append( block )
    BlockRegistry.append( block )
    
    if isinstance( block, NifFormat.NiNode ):
        for child in block.children:
            if not child: continue
            AddBlock( child )
