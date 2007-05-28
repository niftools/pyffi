# run the stripifier on all triangles from nif files
# also useful for profiling

from NifFormat.PyTriStrip import PyTriStrip
from NifFormat.NifFormat import NifFormat

def testBlock(block, verbose):
    if not isinstance(block, NifFormat.NiTriShapeData): return
    print 'calculating strips',
    triangles = [[t.v1, t.v2, t.v3] for t in block.triangles]
    try:
        strips = PyTriStrip.strippify(triangles)
        for strip in strips:
            print len(strip),
        print
    except StandardError:
        print 'failed to strip triangles'
        print triangles
        raise

    print 'checking triangles'
    try:
        triangles2 = PyTriStrip.triangulate(strips)
    except StandardError:
        print 'failed to triangulate strips'
        print strips
        raise

    for t0, t1, t2 in triangles2:
        if [t0, t1, t2] not in triangles and [t1, t2, t0] not in triangles and [t2, t0, t1] not in triangles:
            print strips
            print triangles
            print [t0, t1, t2], 'in strip but not in triangles'
            raise ValueError('strippification invalid?')

    for t0, t1, t2 in triangles:
        if [t0, t1, t2] not in triangles2 and [t1, t2, t0] not in triangles2 and [t2, t0, t1] not in triangles2:
            print strips
            print triangles
            print [t0, t1, t2], 'in triangles but not in strip'
            raise ValueError('strippification invalid?')
