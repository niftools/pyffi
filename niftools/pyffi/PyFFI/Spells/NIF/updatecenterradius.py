# run the stripifier on all triangles from nif files
# also useful for profiling

from PyFFI.Formats.NIF import NifFormat

__readonly__ = False

def testBlock(block, **args):
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    if block.data:
        print "recalculating center and radius"
        block.data.updateCenterRadius()
    if block.isSkin():
        print "recalculating skin center and radius"
        block.updateSkinCenterRadius()

