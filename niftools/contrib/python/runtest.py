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
ctrl.target = blk
blk.controller = ctrl

blk.numChildren = 1
blk.children.updateSize()
strips = NifFormat.NiTriStrips()
blk.children[0] = strips

data = NifFormat.NiTriStripsData()
strips.data = data

data.numVertices = 5
data.hasVertices = True
data.vertices.updateSize()
for i, v in enumerate(data.vertices):
    v.x = 1.0+i/10.0
    v.y = 0.2+1.0/(i+1)
    v.z = 0.03
data.numStrips = 2
data.stripLengths.updateSize()
data.stripLengths[0] = 3
data.stripLengths[1] = 4
data.hasPoints = True
data.points.updateSize()
data.points[0][0] = 0
data.points[0][1] = 1
data.points[0][2] = 2
data.points[1][0] = 1
data.points[1][1] = 2
data.points[1][2] = 3
data.points[1][3] = 4

print blk

print data.triangles

print blk.getLinks(0x14000005, 11)
print ctrl.getLinks(0x14000005, 11)
print blk.getRefs(0x14000005, 11)
print ctrl.getRefs(0x14000005, 11)

print blk.translation.asList()

print "Writing nif file"

f = open("test.nif", "wb")
NifFormat.write(0x14000005, 11, f, [blk, NifFormat.NiNode()])

# reading a nif file

from cStringIO import StringIO

f = open("test.nif", "rb")
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
