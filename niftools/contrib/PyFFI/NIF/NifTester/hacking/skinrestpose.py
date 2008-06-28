# simply prints a skin's rest pose and first frame of animation, for comparison

from PyFFI.Formats.NIF import NifFormat

def testBlock(block, **args):
    if not isinstance(block, NifFormat.NiGeometry): return
    if block.skinInstance == None: return
    try:
        block._validateSkin()
    except ValueError:
        print "* %s: warning, invalid skin structure" % block.name
        return
    dct = block.getBoneRestPositions()
    print "* %s:" % block.name
    for bone, m in dct.items():
        print "BONE %s" % bone.name
        print "REST POSITION (skeleton root coordinates)"
        print str(m)
        print "FIRST FRAME POSITION (skeleton root coordinates)"
        print bone.getTransform(block.skinInstance.skeletonRoot)
