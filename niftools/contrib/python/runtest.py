from NifFormat.NifFormat import NifFormat
from FileFormat.HexDump import HexDump

# checking all supported versions

print "Supported versions:"
for vstr, vnum in sorted(NifFormat.versions.items(), cmp=lambda x, y: cmp(x[1],y[1])):
    print "0x%08X %s"%(vnum, vstr)

# creating new nif blocks

#print "Constructing nif tree"
blk = NifFormat.NiNode()
blk.scale = 2.4
blk.translation.x = 3.9

ctrl = NifFormat.NiVisController()
ctrl.flags = 0x000c
blk.controller = ctrl

blk.numChildren = 1
blk.children.updateSize()
blk.children[0] = NifFormat.NiNode()

print blk

#print "Writing nif file"
#
#f = open("test.nif", "wb")
#NifFormat.write(0x14000005, 0, f, [blk, NifFormat.NiNode()])

# reading a nif file

from cStringIO import StringIO

f = open("cube.nif", "rb")
try:
    buffer = StringIO(f.read(-1))
finally:
    f.close()
try:
    version, user_version = NifFormat.getVersion(buffer)
    if version >= 0:
        try:
            print "reading nif file (version 0x%08X)"%version
            NifFormat.read(version, user_version, buffer)
        except:
            HexDump(buffer)
            raise
    elif version == -1:
        print 'nif version not supported'
    else:
        print 'not a nif file'
finally:
    buffer.close()
