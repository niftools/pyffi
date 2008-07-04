"""Recalculate center and radius calculation (including skin center and
radius).
"""

from PyFFI.Formats.NIF import NifFormat

__readonly__ = False

def testBlock(block, **args):
    """Recalculate the center and radius.

    @param block: The block to test.
    @type block: L{NifFormat.NiTriBasedGeom}
    """
    if not isinstance(block, NifFormat.NiTriBasedGeom):
        return
    if block.data:
        print "recalculating center and radius"
        block.data.updateCenterRadius()
    if block.isSkin():
        print "recalculating skin center and radius"
        block.updateSkinCenterRadius()

