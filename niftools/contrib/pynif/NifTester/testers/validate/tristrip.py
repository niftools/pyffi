# run the stripifier on all triangles from nif files
# also useful for profiling

from NifFormat.PyTriStrip import PyTriStrip
from NifFormat.NifFormat import NifFormat

def testBlock(block, verbose):
    if not isinstance(block, NifFormat.NiTriShapeData): return
    print 'calculating strips'
    triangles = [[t.v1, t.v2, t.v3] for t in block.triangles]
    try:
        strips = PyTriStrip.stripify(triangles)
    except StandardError:
        print 'failed to strip triangles'
        print triangles
        raise

    print 'checking triangles'
    PyTriStrip._checkStrips(triangles, strips)
