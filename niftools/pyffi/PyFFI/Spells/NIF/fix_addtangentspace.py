"""Check tangent space and tangent space calculation."""

from PyFFI.Formats.NIF import NifFormat

import struct

# flag overwrite
__readonly__ = False

def testBlock(block, **args):
    """Add tangentspace if it is missing.

    @param block: The block to test.
    @type block: L{NifFormat.NiTriBasedGeom}
    """
    # does it apply on this block?
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    # does this block have tangent space data?
    for extra in block.getRefs():
        if isinstance(extra, NifFormat.NiBinaryExtraData):
            if extra.name == 'Tangent space (binormal & tangent vectors)':
                return

    print("no tangent space in block '%s', adding one..." % block.name)

    # recalculate the tangent space
    block.updateTangentSpace()

