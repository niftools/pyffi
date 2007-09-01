from PyFFI.NIF import NifFormat

def testBlock(block, verbose):
    if not isinstance(block, NifFormat.bhkMoppBvTreeShape): return
    print "found a mopp"

    mopp = [b for b in block.moppData]
    o = NifFormat.Vector3()
    o.x = block.origin.x
    o.y = block.origin.y
    o.z = block.origin.z
    scale = block.scale

    print "recalculating mopp origin and scale"
    block.updateOriginScale()
    print "(origin  was %s and is now %s)"%(o, block.origin)
    print "(scale was %s and is now %s)"%(scale,block.scale)

    if block.origin != o: raise ValueError("origin not correctly recalculated")
    if abs(block.scale - scale) > 0.1: raise ValueError("scale not correctly recalculated")

    print "parsing mopp"
    # n = number of bytes, tris = triangle indices
    n, tris = block.parseTree(verbose = True)

    # check triangles
    counts = [ tris.count(i) for i in xrange(block.shape.data.numTriangles) ]
    missing = [ i for i in xrange(block.shape.data.numTriangles) if counts[i] != 1 ]
    if missing:
        print "mopp parse error"
        print "triangles index, times parsed (each index should be parsed exactly once)"
        for i in missing:
            print i, counts[i]
        raise ValueError("mopp parsing failed")

    # check size
    if n != block.moppDataSize:
        raise ValueError("mopp parsing failed; incorrect number of bytes processed (number of bytes %i, processed %i)"%(block.moppDataSize,n))

