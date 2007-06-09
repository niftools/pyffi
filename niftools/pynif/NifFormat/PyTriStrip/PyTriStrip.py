USE_NVTRISTRIP = False

if USE_NVTRISTRIP:
    import NvTriStrip
else:
    from TriangleStripifier import TriangleStripifier
    from TriangleMesh import FaceEdgeMesh

def triangulate(strips):
    """A generator for iterating over the faces in a set of
    strips. Degenerate triangles in strips are discarded.

    >>> triangulate([[1, 0, 1, 2, 3, 4, 5, 6]])
    [[0, 2, 1], [1, 2, 3], [2, 4, 3], [3, 4, 5], [4, 6, 5]]
    """

    triangles = []

    for strip in strips:
        i = strip.__iter__()
        j = False
        t1, t2 = i.next(), i.next()
        for k in xrange(2, len(strip)):
            j = not j
            t0, t1, t2 = t1, t2, i.next()
            if t0 == t1 or t1 == t2 or t2 == t0: continue
            triangles.append([t0, t1, t2] if j else [t0, t2, t1])

    return triangles

def _generateFacesFromTriangles(triangles):
    i = triangles.__iter__()
    while True:
        yield [i.next(), i.next(), i.next()]

def _checkStrips(triangles, strips):
    strips_triangles = triangulate(strips)
    for t0,t1,t2 in triangles:
        if t0 == t1 or t1 == t2 or t2 == t0: continue
        if [t0,t1,t2] not in strips_triangles and [t1,t2,t0] not in strips_triangles and [t2,t0,t1] not in strips_triangles:
            raise ValueError('triangle %s in triangles but not in strips\ntriangles = %s\nstrips = %s'%([t0,t1,t2],triangles,strips))
    for t0,t1,t2 in strips_triangles:
        if t0 == t1 or t1 == t2 or t2 == t0: continue
        if [t0,t1,t2] not in triangles and [t1,t2,t0] not in triangles and [t2,t0,t1] not in triangles:
            raise ValueError('triangle %s in strips but not in triangles\ntriangles = %s\nstrips = %s'%([t0,t1,t2],triangles,strips))

def strippify(triangles):
    """Converts triangles into a list of strips.

    >>> triangles = [[0,1,4],[1,2,4],[2,3,4],[3,0,4]]
    >>> strips = strippify(triangles)
    >>> _checkStrips(triangles, strips)
    >>> triangles = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23]]
    >>> strips = strippify(triangles)
    >>> _checkStrips(triangles, strips)
    >>> triangles = [[0, 1, 2], [0, 1, 2]]
    >>> strips = strippify(triangles)
    >>> _checkStrips(triangles, strips)
    >>> triangles = [[0, 1, 2], [2, 1, 0]]
    >>> strips = strippify(triangles)
    >>> _checkStrips(triangles, strips)
    >>> triangles = [[0, 1, 2], [2, 1, 0], [1, 2, 3]]
    >>> strips = strippify(triangles)
    >>> _checkStrips(triangles, strips) # NvTriStrip gives wrong result
    >>> triangles = [[0, 1, 2], [0, 1, 3]]
    >>> strips = strippify(triangles)
    >>> _checkStrips(triangles, strips) # NvTriStrip gives wrong result
    >>> triangles = [[1, 5, 2], [5, 2, 6], [5, 9, 6], [9, 6, 10], [9, 13, 10], [13, 10, 14], [0, 4, 1], [4, 1, 5], [4, 8, 5], [8, 5, 9], [8, 12, 9], [12, 9, 13], [2, 6, 3], [6, 3, 7], [6, 10, 7], [10, 7, 11], [10, 14, 11], [14, 11, 15]]
    >>> strips = strippify(triangles)
    >>> _checkStrips(triangles, strips) # NvTriStrip gives wrong result
    """

    if USE_NVTRISTRIP:
        lst = []
        for face in triangles:
            lst.extend(face)
        pgroups = NvTriStrip.GenerateStrips(lst, validateEnabled = False)
        strips = []
        for ptype, indices in pgroups:
            if ptype == NvTriStrip.PT_STRIP:
                strips.append(indices)
            else:
                raise RuntimeError("unexpected primitive group type %i (bug!)"%ptype)
        return strips
    else:
        # build a mesh from triangles
        mesh = FaceEdgeMesh()
        for face in triangles:
            mesh.AddFace(*face)

        # calculate the strip
        stripifier = TriangleStripifier()
        stripifier.GLSelector.MinStripLength = 0
        stripifier(mesh)

        # add the triangles to it
        i = stripifier.TriangleList.__iter__()
        return [face for face in _generateFacesFromTriangles(stripifier.TriangleList)] + stripifier.TriangleStrips

if __name__=='__main__':
    import doctest
    doctest.testmod()
