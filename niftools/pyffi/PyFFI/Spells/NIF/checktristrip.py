"""Run the stripifier on all triangles from nif files. This spell is also
useful for doublechecking and profiling the stripifier and stitcher/unstitcher.
"""

from PyFFI.Utils import TriStrip
from PyFFI.Formats.NIF import NifFormat

def testBlock(block, **args):
    """Restripify the geometry, compare the strip to the original geometry,
    stitch and unstitch, and report accordingly.

    @param block: The block to stripify.
    @type block: L{NifFormat.NiTriShapeData}
    """
    if not isinstance(block, NifFormat.NiTriShapeData):
        return
    print('calculating strips')
    triangles = [(t.v1, t.v2, t.v3) for t in block.triangles]
    try:
        strips = TriStrip.stripify(triangles, stitchstrips = False)
    except StandardError:
        print('failed to strip triangles')
        print(triangles)
        raise

    print('checking strip triangles')
    TriStrip._checkStrips(triangles, strips)

    print('checking stitched strip triangles')
    stitchedstrip = TriStrip.stitchStrips(strips)
    TriStrip._checkStrips(triangles, [stitchedstrip])

    print('checking unstitched strip triangles')
    unstitchedstrips = TriStrip.unstitchStrip(stitchedstrip)
    TriStrip._checkStrips(triangles, unstitchedstrips)

