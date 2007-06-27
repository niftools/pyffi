# check skin partition and skin partition calculation

from PyFFI.NIF import NifFormat

import struct

def testBlock(block, verbose):
    # does it apply on this block?
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    # does this block have a skin?
    if not block.skinInstance: return

    print "found skin in block '%s'"%block.name
    block._validateSkin()
    skininst = block.skinInstance
    skinpart = skininst.skinPartition

    # TODO copy the skin partition data

    print 'lost weight from partitioning', block.updateSkinPartition(maxbonesperpartition = 4, maxbonespervertex = 4)

    # TODO check the skin partition data
