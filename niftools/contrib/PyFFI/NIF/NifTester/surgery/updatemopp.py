from PyFFI.Formats.NIF import NifFormat

def testBlock(block, **args):
    if not isinstance(block, NifFormat.bhkMoppBvTreeShape): return
    print "mopp length = %i"%block.moppDataSize
    print "updating mopp data..."
    block.updateOriginScale()
    block.updateMopp()
    print "mopp length = %i"%block.moppDataSize
