# checks whether the NiSkinData transforms are calculated correctly

# the left hand side of some of the better bodies skins do not satisfy the
# calculations below...

from PyFFI.NIF import NifFormat

def testBlock(block, **args):
    # does it apply?
    if not isinstance( block, NifFormat.NiGeometry ): return
    if block.skinInstance == None: return
    try:
        block._validateSkin()
    except ValueError:
        print "* %s: warning, invalid skin structure" % block.name
        return
    # calculate the skin instance skeleton root offset
    skininst = block.skinInstance
    skindata = skininst.data
    skelroot = skininst.skeletonRoot
    m = skininst.data.getTransform().getInverse()
    n = block.getTransform(skelroot)
    if m != n:
        print "* %s:"%block.name
        print "bad skinInstance.data transform"
        print "calculated:"
        print n
        print "effective:"
        print m
        return # do not checking bone offsets if global offset is already wrong

    return # disable bone rest position check

    # calculate bone rest positions
    # this is just for play
    # usually the rest pose is not stored in the bone transform
    for i, bone_block in enumerate(block.skinInstance.bones): 
        m = skindata.boneList[i].getTransform().getInverse() * skininst.data.getTransform().getInverse()
        n = bone_block.getTransform(skelroot)
        if m != n:
            print "* %s:"%bone_block.name
            print "bone matrix is not aligned"
            print "first frame:"
            print n
            print "rest pose:"
            print m
        else:
            print "* %s:"%bone_block.name
            print "bone matrix is aligned"
