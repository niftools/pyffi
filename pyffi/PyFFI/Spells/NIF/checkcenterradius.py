"""Check center and radius calculation."""

# tentative results
# -----------------
# oblivion: ok
# civ4: mostly ok (with very few exceptions: effects/magpie/flock.nif, units/!errorunit/bear.nif, maybe some more)
# daoc: ok
# morrowind: usually ok (quite some exceptions here)
# zoo tycoon 2: mostly ok (except *_Adult_*.nif files)

from PyFFI.Formats.NIF import NifFormat

def testBlock(block, **args):
    """Recalculate the center and radius,
    compare them to the originals, and report accordingly.

    @param block: The block to test.
    @type block: L{NifFormat.NiGeometry}
    """
    if not isinstance(block, NifFormat.NiGeometry):
        return

    print("checking %s" % block.name)
    geomdata = block.data

    #print("getting bounding sphere")
    center = NifFormat.Vector3()
    center.x = geomdata.center.x
    center.y = geomdata.center.y
    center.z = geomdata.center.z
    radius = geomdata.radius

    #print("checking all vertices are inside")
    maxr = 0.0
    maxv = None
    for vert in geomdata.vertices:
        dist = vert - center
        if dist * dist > maxr:
            maxr = dist * dist
            maxv = vert
    maxr = maxr ** 0.5

    if maxr > 1.01 * radius + NifFormat._EPSILON:
       raise ValueError(
           "not all vertices inside bounding sphere (vertex %s, error %s)"
           % (v, abs(maxr - radius)))
       #print(
       #    "!!! not all vertices inside bounding sphere (vertex %s, error %s)"
       #    % (v, abs(maxr - radius)))

    #print("recalculating bounding sphere")
    geomdata.updateCenterRadius()

    #print("comparing old bounding sphere with new bounding sphere")
    if center != geomdata.center:
       print(
           "center does not match; original %s, calculated %s"
           % (center, geomdata.center))
    if abs(radius - geomdata.radius) > NifFormat._EPSILON:
       print("radius does not match; original %s, calculated %s"%(radius, geomdata.radius))
    #print("perfect match!")

