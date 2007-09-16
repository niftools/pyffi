# run the stripifier on all triangles from nif files
# also useful for profiling

from PyFFI.NIF import NifFormat

def testBlock(block, verbose):
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    if block.data:
        print "recalculating center and radius"
        block.data.updateCenterRadius()
    if block.isSkin():
        print "recalculating skin center and radius"
        block.updateSkinCenterRadius()

def testFile(version, user_version, f, roots, verbose):
    f.seek(0)
    NifFormat.write(version, user_version, f, roots)

