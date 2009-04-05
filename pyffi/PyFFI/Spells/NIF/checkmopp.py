"""Check a mopp origin and scale, parse it, check if all the mopp code was
parsed, and check that all triangles are visited.
"""

from PyFFI.Formats.NIF import NifFormat

def testBlock(block, **args):
    """Check a mopp origin and scale, parse it, check if all the mopp code was
    parsed, and check that all triangles are visited.

    @param block: The block to test.
    @type block: L{NifFormat.bhkMoppBvTreeShape}
    """
    if not isinstance(block, NifFormat.bhkMoppBvTreeShape):
        return
    print("found a mopp")

    mopp = [b for b in block.moppData]
    o = NifFormat.Vector3()
    o.x = block.origin.x
    o.y = block.origin.y
    o.z = block.origin.z
    scale = block.scale

    print("recalculating mopp origin and scale")
    block.updateOriginScale()
    print("(origin  was %s and is now %s)" % (o, block.origin))
    print("(scale was %s and is now %s)" % (scale,block.scale))

    if block.origin != o:
        raise ValueError("origin not correctly recalculated")
    if abs(block.scale - scale) > 0.5:
        raise ValueError("scale not correctly recalculated")

    print("parsing mopp")
    # ids = indices of bytes processed, tris = triangle indices
    ids, tris = block.parseMopp(verbose = True)

    error = False

    # check triangles
    counts = [tris.count(i) for i in xrange(block.shape.data.numTriangles)]
    missing = [i for i in xrange(block.shape.data.numTriangles)
               if counts[i] != 1]
    if missing:
        print("some triangles never visited, or visited more than once")
        print("triangles index, times visited")
        for i in missing:
            print(i, counts[i])
        error = True

    wrong = [i for i in tris if i > block.shape.data.numTriangles]
    if wrong:
        print("invalid triangle indices")
        print(wrong)
        error = True

    # check bytes
    counts = [ids.count(i) for i in xrange(block.moppDataSize)]
    missing = [i for i in xrange(block.moppDataSize) if counts[i] != 1]
    if missing:
        print("some bytes never visited, or visited more than once")
        print("byte index, times visited, value")
        for i in missing:
            print(i, counts[i], "0x%02X" % mopp[i])
            print([mopp[k] for k in xrange(i, min(block.moppDataSize, i + 10))])
        error = True

    if error:
        raise ValueError("mopp parsing failed")

