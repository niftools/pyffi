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
        # adapt calculated inertia matrix with observed mass
        if mass > 0.001:
            correction = mass / block.mass
            for i in xrange(12):
                block.inertia[i] *= correction
    else:
        print "perfect match!"

    print "checking center..."
    if center != block.center:
        #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
        print("warning: center does not match; original %s, calculated %s"%(center, block.center))
    else:
        print "perfect match!"

    print "checking inertia..."

    scale = max(abs(x) for x in inertia + [ y for y in block.inertia ])
    if max(abs(x - y) for x, y in zip(inertia, block.inertia)) > 0.1 * scale:
        #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
        print("warning: inertia does not match:\n\noriginal\n%s\n\ncalculated\n%s\n"%(inertia, [x for x in block.inertia]))
    else:
        print "perfect match!"
