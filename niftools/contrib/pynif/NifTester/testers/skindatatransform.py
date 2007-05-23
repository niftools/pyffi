# checks whether the NiSkinData transform matrix is not identity
# (the Morrowind better bodies meshes have positive result on this test)

from NifFormat.NifFormat import NifFormat

def isApplicable( block ):
    return isinstance( block, NifFormat.NiSkinData )


def Run( block ):
    m = block.getTransform()
    return not m.isIdentity()


def Result( block ):
    m = block.getTransform()
    return "* %s:\n%s" % ( block.__class__.__name__, m )
