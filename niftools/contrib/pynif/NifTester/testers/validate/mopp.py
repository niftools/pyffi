from PyFFI.NIF import NifFormat

def testBlock(block, verbose):
    if not isinstance(block, NifFormat.bhkMoppBvTreeShape): return
    print "found a mopp"
    block.printTree()

    tree = block.getTree()

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

    print "resetting tree"
    block.setTree(tree)

    if len(mopp) != block.moppDataSize:
        block.printTree()
        raise ValueError("mopp set failed; tree was modified")

    for b1, b2 in zip(mopp, block.moppData):
        if b1 != b2:
            block.printTree()
            raise ValueError("mopp set failed; tree was modified")

