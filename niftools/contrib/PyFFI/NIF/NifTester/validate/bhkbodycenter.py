"""Check bhkRigidBody centers."""

from PyFFI.NIF import NifFormat

def testBlock(block, **args):
    if not isinstance(block, NifFormat.bhkRigidBody): return

    print "getting rigid body mass, center, and inertia"
    mass = block.mass
    center = block.center.getCopy()
    inertia = block.inertia.getCopy()

    print "recalculating..."
    block.updateMassCenterInertia(mass = block.mass)

    #print "checking mass..."
    #if mass != block.mass:
    #    #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
    #    print("warning: mass does not match; original %s, calculated %s"%(mass, block.mass))
    #    # adapt calculated inertia matrix with observed mass
    #    if mass > 0.001:
    #        correction = mass / block.mass
    #        for i in xrange(12):
    #            block.inertia[i] *= correction
    #else:
    #    print "perfect match!"

    print "checking center..."
    if center != block.center:
        #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
        print("warning: center does not match; original %s, calculated %s"%(center, block.center))
    else:
        print "perfect match!"

    print "checking inertia..."

    scale = max(max(abs(x) for x in row) for row in inertia.asList() + block.inertia.asList())
    if max(max(abs(x - y) for x, y in zip(row1, row2)) for row1, row2 in zip(inertia.asList(), block.inertia.asList())) > 0.1 * scale:
        #raise ValueError("center does not match; original %s, calculated %s"%(center, block.center))
        print("warning: inertia does not match:\n\noriginal\n%s\n\ncalculated\n%s\n"%(inertia, block.inertia))
    else:
        print "perfect match!"
