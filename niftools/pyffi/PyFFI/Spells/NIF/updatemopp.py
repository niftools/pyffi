from PyFFI.NIF import NifFormat

__readonly__ = False

def testBlock(block, **args):
    if not isinstance(block, NifFormat.bhkMoppBvTreeShape): return
    print "mopp length = %i"%block.moppDataSize
    print "updating mopp data..."
    block.updateOriginScale()
    block.updateMopp()
    print "mopp length = %i"%block.moppDataSize
