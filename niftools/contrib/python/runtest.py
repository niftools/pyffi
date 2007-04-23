from NifFormat.NifFormat import NifFormat

print "Supported versions:"
for vstr, vnum in NifFormat.versions.items():
    print "0x%08X %s"%(vnum, vstr)

print "Default NiNode block"
blk = NifFormat.NiNode()
blk.scale = 2.4
blk.translation.x = 3.9

ctrl = NifFormat.NiVisController()
ctrl.flags = 0x000c
blk.controller = ctrl

print blk

print "Default header"
hdr = NifFormat.Header()
hdr.headerString = "hello world!"
print hdr
