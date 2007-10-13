# run the stripifier on all triangles from nif files
# also useful for profiling

from PyFFI.Utils import PyTriStrip
from PyFFI.NIF import NifFormat

def testBlock(block, **args):
    if not isinstance(block, NifFormat.NiTriShapeData): return
    print 'calculating strips'
    triangles = [[t.v1, t.v2, t.v3] for t in block.triangles]
    try:
        strips = PyTriStrip.stripify(triangles, stitchstrips = False)
    except StandardError:
        print 'failed to strip triangles'
        print triangles
        raise

    print 'checking strip triangles'
    PyTriStrip._checkStrips(triangles, strips)

    print 'checking stitched strip triangles'
    stitchedstrip = PyTriStrip.stitchStrips(strips)
    PyTriStrip._checkStrips(triangles, [stitchedstrip])

    print 'checking unstitched strip triangles'
    unstitchedstrips = PyTriStrip.unstitchStrip(stitchedstrip)
    PyTriStrip._checkStrips(triangles, unstitchedstrips)
