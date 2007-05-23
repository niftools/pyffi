from NifFormat.NifFormat import NifFormat

def isApplicable( block ):
    return isinstance( block, NifFormat.bhkRigidBody )


def Run( block ):
    v = block.unknownVector
    result = ( 1E-8 < abs(v.x) ) and ( abs(v.x) < 1E8 )
    if result: return True
    
    result = ( 1E-8 < abs(v.y) ) and ( abs(v.y) < 1E8 )
    if result: return True
    
    result = ( 1E-8 < abs(v.z) ) and ( abs(v.z) < 1E8 )
    if result: return True
    
    return False


def Result( block ):
    v = block.unknownVector
    return "%s - (%.2f, %.2f. %.2f) " % ( block.__class__.__name__, v.x, v.y, v.z )
