"""
Check bhkConvexVerticesShape data.

This test checks whether each vertex is the intersection of at least three planes.
"""

from PyFFI.NIF import NifFormat

def testBlock(block, verbose):
    if not isinstance(block, NifFormat.bhkConvexVerticesShape): return

    print "checking shape"

    for v4 in block.vertices:
        v = NifFormat.Vector3()
        v.x = v4.x
        v.y = v4.y
        v.z = v4.z
        num_intersect = 0
        for n4 in block.normals:
            n = NifFormat.Vector3()
            n.x = n4.x
            n.y = n4.y
            n.z = n4.z
            d   = n4.w
            if abs(v*n+d) < 0.01: num_intersect += 1
        if num_intersect < 3:
            raise ValueError("vertex %s does not intersect with 3 planes")

