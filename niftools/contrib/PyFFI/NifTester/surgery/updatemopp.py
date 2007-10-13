from PyFFI.NIF import NifFormat

def testBlock(block, **args):
    if not isinstance(block, NifFormat.bhkMoppBvTreeShape): return
    print "mopp length = %i"%block.moppDataSize
    print "updating mopp data..."
    block.updateOriginScale()
    block.updateMopp()
    print "mopp length = %i"%block.moppDataSize

def testFile(version, user_version, f, roots, **args):
    f.seek(0)
    NifFormat.write(version, user_version, f, roots)
    f.truncate()

