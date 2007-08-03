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

    lw = block.updateSkinPartition(maxbonesperpartition = 4, maxbonespervertex = 4, verbose = verbose)
    print 'lost weight from partitioning', lw
    if lw > 0.49: raise ValueError('lost too much weight; bug in partition algorithm?')

    # TODO check the skin partition data
