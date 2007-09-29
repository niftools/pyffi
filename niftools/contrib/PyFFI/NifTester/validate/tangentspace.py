# check tangent space and tangent space calculation

from PyFFI.NIF import NifFormat

import struct

def bytestovectors(bytes):
    s = ''
    for b in bytes:
        s += chr(b)
        if len(s) == 12:
            v = NifFormat.Vector3()
            v.x, v.y, v.z = struct.unpack('<fff', s)
            yield v
            s = ''

def testBlock(block, verbose):
    # does it apply on this block?
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    # does this block have tangent space data?
    for extra in block.getRefs():
        if isinstance(extra, NifFormat.NiBinaryExtraData):
            if extra.name == 'Tangent space (binormal & tangent vectors)':
                break
    else:
        return

    print "found tangent space in block '%s'"%block.name
    # check length
    if 24*block.data.numVertices != extra.binaryData.dataSize:
        raise ValueError('tangent space data has invalid size, expected %i bytes but got %i'%(24*block.data.numVertices,extra.binaryData.dataSize))
    # copy the tangent space data
    old_tangentspace = [v for v in bytestovectors(extra.binaryData.data)]
    old_tan = old_tangentspace[:block.data.numVertices]
    old_bin = old_tangentspace[block.data.numVertices:]
    # check orthogonality constraint
    for i, (n, t, b) in enumerate(zip(block.data.normals, old_tan, old_bin)):
        if abs(n*n-1) > NifFormat._EPSILON:
            print ('warning: non-unit normal %s (norm %f) at vertex %i'%(n, (n*n)** 0.5, i))
        if abs(t*t-1) > NifFormat._EPSILON:
            print ('warning: non-unit tangent %s (norm %f) at vertex %i'%(t, (t*t)** 0.5, i))
        if abs(b*b-1) > NifFormat._EPSILON:
            print ('warning: non-unit binormal %s (norm %f) at vertex %i'%(b, (b*b)** 0.5, i))
        if abs(n*t) + abs(n*b) > NifFormat._EPSILON:
            volume = n*t.crossproduct(b)
            print 'warning: non-ortogonal tangent space at vertex %i'%i
            print 'n * t = %s * %s = %f'%(n,t,n*t)
            print 'n * b = %s * %s = %f'%(n,b,n*b)
            print 't * b = %s * %s = %f'%(t,b,t*b)
            print 'volume = %f'%volume

    # recalculate the tangent space
    block.updateTangentSpace()
    # copy the tangent space data
    new_tangentspace = [v for v in bytestovectors(extra.binaryData.data)]
    new_tan = new_tangentspace[:block.data.numVertices]
    new_bin = new_tangentspace[block.data.numVertices:]
    # compare the two spaces
    multiplicity = [0]*block.data.numVertices
    for tri in block.data.getTriangles():
        for t in tri:
            multiplicity[t] += 1
    for i, (t,b,tt,bb) in enumerate(zip(old_tan, old_bin, new_tan, new_bin)):
        #if multiplicity[i] > 1: continue # uncomment to check only vertices that belong to a single triangle
        for old_f, new_f in zip(t.asList() + b.asList(), tt.asList() + bb.asList()):
            if abs(old_f - new_f) > 0.3: #NifFormat._EPSILON:
                #print old_tangentspace
                #print new_tangentspace
                print 'old vectors', t, b #[repr(x) for x in t.asList()], [repr(x) for x in b.asList()]
                print 'new vectors', tt, bb #[repr(x) for x in tt.asList()], [repr(x) for x in bb.asList()]
                print ('calculated tangent space differs from original at vertex %i'%i)
                break
