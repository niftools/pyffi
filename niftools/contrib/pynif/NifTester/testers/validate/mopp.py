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

    if n != block.moppDataSize:
        raise ValueError("mopp parsing failed; not all bytes processed")

