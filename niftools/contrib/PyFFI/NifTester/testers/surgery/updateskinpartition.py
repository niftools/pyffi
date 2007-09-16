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
    if not skinpart:
        skinpart = skininst.data.skinPartition

    block.updateSkinPartition(maxbonesperpartition = 4, maxbonespervertex = 4, stripify = False, verbose = verbose, padbones = True)

    #print skininst.data.skinPartition

def testFile(version, user_version, f, roots, verbose, arg = None):
    f.seek(0)
    NifFormat.write(version, user_version, f, roots)
    f.truncate()

