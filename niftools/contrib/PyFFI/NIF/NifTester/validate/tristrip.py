# run the stripifier on all triangles from nif files
# also useful for profiling

from PyFFI.Utils import TriStrip
from PyFFI.Formats.NIF import NifFormat

def testBlock(block, **args):
    if not isinstance(block, NifFormat.NiTriShapeData): return
    print 'calculating strips'
    triangles = [(t.v1, t.v2, t.v3) for t in block.triangles]
    try:
        strips = TriStrip.stripify(triangles, stitchstrips = False)
    except StandardError:
        print 'failed to strip triangles'
        print triangles
        raise

    print 'checking strip triangles'
    TriStrip._checkStrips(triangles, strips)

    print 'checking stitched strip triangles'
    stitchedstrip = TriStrip.stitchStrips(strips)
    TriStrip._checkStrips(triangles, [stitchedstrip])

    print 'checking unstitched strip triangles'
    unstitchedstrips = TriStrip.unstitchStrip(stitchedstrip)
    TriStrip._checkStrips(triangles, unstitchedstrips)
