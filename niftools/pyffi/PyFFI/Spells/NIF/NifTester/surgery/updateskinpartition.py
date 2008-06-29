# check skin partition and skin partition calculation

from PyFFI.Formats.NIF import NifFormat

import struct

def testBlock(block, **args):
    verbose = args.get('verbose', 0)
    # does it apply on this block?
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    # does this block have a skin?
    if not block.skinInstance: return

    print "found skin in block '%s'"%block.name
    block._validateSkin()
    skininst = block.skinInstance
    skinpart = skininst.skinPartition
    if not skinpart:
        skinpart = skininst.data.skinPartition

    block.updateSkinPartition(maxbonesperpartition = 4, maxbonespervertex = 4, stripify = False, verbose = verbose, padbones = True)

    #print skininst.data.skinPartition

