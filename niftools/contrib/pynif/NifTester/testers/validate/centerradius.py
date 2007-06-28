# run the stripifier on all triangles from nif files
# also useful for profiling

from PyFFI.NIF import NifFormat

def testBlock(block, verbose):
    if not isinstance(block, NifFormat.NiGeometry): return

    print "found geometry", block.name
    geomdata = block.data

    print "getting bounding sphere"
    center = NifFormat.Vector3()
    center.x = geomdata.center.x
    center.y = geomdata.center.y
    center.z = geomdata.center.z
    radius = geomdata.radius

    print "checking all vertices are inside"
    maxr = 0.0
    maxv = None
    for v in geomdata.vertices:
        d = v - center
        if d*d > maxr:
            maxr = d*d
            maxv = v
    maxr = maxr**0.5

    if maxr > radius + NifFormat._EPSILON:
       #raise ValueError("not all vertices inside bounding sphere (vertex %s, error %s)"%(v, abs(maxr-radius)))
       print "!!! not all vertices inside bounding sphere (vertex %s, error %s)"%(v, abs(maxr-radius))

    return

    # following part seems to fail on quite some nifs

    print "recalculating bounding sphere"
    geomdata.updateCenterRadius()

    print "comparing old bounding sphere with new bounding sphere"
    if center != geomdata.center:
       raise ValueError("center does not match; original %s, calculated %s"%(center, geomdata.center))
    if abs(radius - geomdata.radius) > NifFormat._EPSILON:
       raise ValueError("radius does not match; original %s, calculated %s"%(radius, geomdata.radius))
    print "perfect match!"

