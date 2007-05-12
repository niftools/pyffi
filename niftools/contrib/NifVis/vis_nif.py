from NifFormat.NifFormat import NifFormat

import inspect

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
    
    Refs = GetRefs( block )
    
    for child in Refs:
        if not child in BlockRegistry: AddBlock( child )


def GetRefs( cls, ParentRefs = None ):
    if ParentRefs:
        Refs = ParentRefs
    else:
        Refs = []
    
    CheckList = []
    
    if isinstance( cls, list ):
        CheckList = cls
    elif isinstance( cls, NifFormat.NiObject ):
        for i in inspect.getmembers( cls ):
            if i[0].startswith( '_' ): continue
            CheckList.append( i[1] )
    else:
        return Refs
    
    for c in CheckList:
        if isinstance( c, NifFormat.NiObject ):
            if not c in Refs: Refs.append( c )
        
        elif isinstance( c, NifFormat.Ref ):
            if not c in Refs: Refs.append( c )
        
        elif isinstance( c, list ):
            Refs = GetRefs( c, Refs )
    
    return Refs
