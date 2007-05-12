Registry = {}

def Get( block ):
    if Registry.has_key( block ):
        return Registry[block]
    return None



import sys, os

lizerPath = os.path.dirname( __file__ )
sys.path.append( lizerPath )

for f in os.listdir( lizerPath ):
    module_name, ext = os.path.splitext( f )
    if module_name.startswith( '__' ): continue
    if ext == '.py':
        print 'Imported Lizer: %s' % ( module_name )
        module = __import__( module_name )
        Registry[module_name] = module
