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
    for extra in block.getExtraDatas():
        if isinstance(extra, NifFormat.NiBinaryExtraData):
            if extra.name == 'Tangent space (binormal & tangent vectors)':
                block.removeExtraData(extra)
                print("removing tangent space from block '%s'" % block.name)

