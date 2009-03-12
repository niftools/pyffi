"""Recalculate mopp origin and scale, and generate heuristic mopp code.
This spell can be used to check the mopp generation algorithm with new
geometry.
"""

from PyFFI.Formats.NIF import NifFormat

__readonly__ = False

def testBlock(block, **args):
    """Recalculate mopp origin and scale, and generate heuristic mopp code.

    @param block: The block to test.
    @type block: L{NifFormat.bhkMoppBvTreeShape}
    """
    if not isinstance(block, NifFormat.bhkMoppBvTreeShape):
        return
    print("mopp length = %i" % block.moppDataSize)
    print("updating mopp data...")
    block.updateMopp()
    print("mopp length = %i" % block.moppDataSize)

