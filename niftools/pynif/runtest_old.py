from NifFormat.NifFormat import NifFormat
from FileFormat.Utils import hexDump

# checking all supported versions

print "Supported versions:"
for vstr, vnum in sorted(NifFormat.versions.items(), cmp=lambda x, y: cmp(x[1],y[1])):
    print "0x%08X %s"%(vnum, vstr)

# creating new nif blocks

#print "Constructing nif tree"
root = NifFormat.NiNode()

blk = NifFormat.NiNode()
root.addChild(blk)

blk.scale = 2.4
blk.translation.x = 3.9
blk.rotation.m11 = 1.0
blk.rotation.m22 = 1.0
blk.rotation.m33 = 1.0

ctrl = NifFormat.NiVisController()
ctrl.flags = 0x000c
ctrl.target = blk
blk.controller = ctrl

strips = NifFormat.NiTriStrips()
blk.addChild(strips)

strips.name = "hello world"
strips.rotation.m11 = 1.0
strips.rotation.m22 = 1.0
strips.rotation.m33 = 1.0

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

data.numUvSets = 1
data.hasUv = True
data.uvSets.updateSize()
for i, v in enumerate(data.uvSets[0]):
    v.u = 1.0-i/10.0
    v.v = 1.0/(i+1)

data.hasNormals = True
data.normals.updateSize()
for i, v in enumerate(data.normals):
    v.x = 0.0
    v.y = 0.0
    v.z = 1.0

strips.updateTangentSpace()

print blk
print blk.getTransform()
print strips.getTransform()
print strips.getTransform(root) # includes the blk transform

print "testing the stripper..."
data.setTriangles([(0,1,4),(1,2,4),(2,3,4),(3,0,4)])
print data

print "finding hello world..."
print blk.find(block_name = "hello world")

print "finding time controller..."
print blk.find(block_type = NifFormat.NiTimeController)

print blk.getLinks(0x14000005, 11)
print ctrl.getLinks(0x14000005, 11)
print blk.getRefs()
print ctrl.getRefs()

print blk.translation.asList()

print blk.findChain(data) # [ninode, nitristrips, nitristripsdata]
print data.findChain(ctrl) # []

print "Writing nif file"

f = open("test.nif", "wb")
NifFormat.write(0x14000005, 11, f, [root, NifFormat.NiNode()])

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
