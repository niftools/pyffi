# checks whether the NiSkinData transform matrix is not identity
# (the Morrowind better bodies meshes have positive result on this test)

from PyFFI.Formats.NIF import NifFormat

def testBlock(block, **args):
    # does it apply?
    if not isinstance( block, NifFormat.NiGeometry ): return
    if block.skinInstance == None: return
    try:
        block._validateSkin()
    except ValueError:
        print("* %s: warning, invalid skin structure" % block.name)
        return
    # do the test
    m = block.skinInstance.data.getTransform()
    if not m.isIdentity():
        print("* %s:\n%s" % ( block.name, m ))
