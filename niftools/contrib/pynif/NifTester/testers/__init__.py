Registry = {}

def Get( block ):
    if Registry.has_key( block ):
        return Registry[block]
    return None



import sys, os

testersPath = os.path.dirname( __file__ )
sys.path.append( testersPath )

for f in os.listdir( testersPath ):
    module_name, ext = os.path.splitext( f )
    if module_name.startswith( '__' ): continue
    if ext == '.py':
        module = __import__( module_name )
        Registry[module_name] = module

print "Imported %d Testers." % len( Registry )
