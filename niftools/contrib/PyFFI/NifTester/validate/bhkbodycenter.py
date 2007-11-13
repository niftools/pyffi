"""Check bhkRigidBody centers."""

from PyFFI.NIF import NifFormat

def testBlock(block, **args):
    if not isinstance(block, NifFormat.bhkRigidBody): return

    print "getting rigid body center"
    center = block.center.getCopy()

    print "recalculating..."
    block.updateCenter()

    print "comparing old with new..."
    if center != block.center:
        #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
        print("warning: center does not match; original %s, calculated %s"%(center, block.center))
    else:
        print "perfect match!"

