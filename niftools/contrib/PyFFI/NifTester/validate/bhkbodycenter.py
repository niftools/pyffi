"""Check bhkRigidBody centers."""

from PyFFI.NIF import NifFormat

def testBlock(block, **args):
    if not isinstance(block, NifFormat.bhkRigidBody): return

    print "getting rigid body mass, center, and inertia"
    mass = block.mass
    center = block.center.getCopy()
    inertia = [ x for x in block.inertia ]

    print "recalculating..."
    block.updateMassCenterInertia(density = 1)

    print "checking mass..."
    if mass != block.mass:
        #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
        print("warning: mass does not match; original %s, calculated %s"%(mass, block.mass))
    else:
        print "perfect match!"

    print "checking center..."
    if center != block.center:
        #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
        print("warning: center does not match; original %s, calculated %s"%(center, block.center))
    else:
        print "perfect match!"

    print "checking inertia..."
    if sum(abs(x - y) for x, y in zip(inertia, block.inertia)) > 0.01:
        #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
        print("warning: inertia does not match; original\n%s, calculated\n%s"%(inertia, [x for x in block.inertia]))
    else:
        print "perfect match!"
