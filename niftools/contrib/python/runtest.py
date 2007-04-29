import gc

from NifFormat.NifFormat import NifFormat

print "Supported versions:"
for vstr, vnum in NifFormat.versions.items():
    print "0x%08X %s"%(vnum, vstr)

print "Constructing nif tree"
blk = NifFormat.NiNode()
blk.scale = 2.4
blk.translation.x = 3.9

ctrl = NifFormat.NiVisController()
ctrl.flags = 0x000c
blk.controller = ctrl

blk.numChildren = 1
blk.children.updateSize()
blk.children[0] = NifFormat.NiNode()

print "Writing nif file"

f = open("test.nif", "wb")
NifFormat.write([blk, NifFormat.NiNode()], f, 0x14000005, 0)

if gc.garbage:
    print "warning: uncollectable objects"
    print gc.garbage
