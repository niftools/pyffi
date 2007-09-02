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

    error = False

    # check triangles
    counts = [ tris.count(i) for i in xrange(block.shape.data.numTriangles) ]
    missing = [ i for i in xrange(block.shape.data.numTriangles) if counts[i] != 1 ]
    if missing:
        print "some triangles never visited, or visited more than once"
        print "triangles index, times visited"
        for i in missing:
            print i, counts[i]
        error = True

    wrong = [ i for i in tris if i > block.shape.data.numTriangles ]
    if wrong:
        print "invalid triangle indices"
        print wrong
        error = True

    # check size
    if n != block.moppDataSize:
        print "incorrect number of bytes processed (number of bytes %i, processed %i)"%(block.moppDataSize,n)
        error = True

    if error:
        raise ValueError("mopp parsing failed")

