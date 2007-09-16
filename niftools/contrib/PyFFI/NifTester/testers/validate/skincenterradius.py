# run the stripifier on all triangles from nif files
# also useful for profiling

from PyFFI.NIF import NifFormat

def testBlock(block, verbose):
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    if not block.isSkin(): return

    print "getting skindata block bounding sphere"
    center = []
    radius = []
    for skindatablock in block.skinInstance.data.boneList:
        center.append(skindatablock.boundingSphereOffset.getCopy())
        radius.append(skindatablock.boundingSphereRadius)

    print "recalculating bounding sphere"
    block.updateSkinCenterRadius()

    print "comparing old bounding sphere with new bounding sphere"
    for i, skindatablock in enumerate(block.skinInstance.data.boneList):
        if center[i] != skindatablock.boundingSphereOffset:
            raise ValueError("center does not match; original %s, calculated %s"%(center[i], skindatablock.boundingSphereOffset))
        if abs(radius[i] - skindatablock.boundingSphereRadius) > NifFormat._EPSILON:
            raise ValueError("radius does not match; original %s, calculated %s"%(radius[i], skindatablock.boundingSphereRadius))
    print "perfect match!"

