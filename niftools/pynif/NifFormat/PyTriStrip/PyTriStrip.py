from TraversalUtilities import Stripifier
from Mesh import Mesh

def _iterateTriangleList(triangles):
    """A generator for iterating over the triangles in a list."""
    i = triangles.__iter__()
    while True:
        yield (i.next(), i.next(), i.next())

def generateTriangles(strip):
    """Converts a strip into a list of triangles. Degenerate triangles are
    discarded."""
    triangles = []
    
    t1 = strip[0]
    t2 = strip[1]
    for i in xrange(2, len(strip)):
        t0 = t1
        t1 = t2
        t2 = strip[i]
        if t0 == t1 or t1 == t2 or t2 == t0: continue
        t = triangles_iter.next()
        if i & 1: triangles.extend([t0,t2,t1])
        else:     triangles.extend([t0,t1,t2])
    return triangles

def generateStrips(triangles, minStripLength = 0):
    """Converts triangles into strips.

    Returns a tuple (triangles, fans, strips) where triangles is a
    list of triangle indices, fans is a list of fans, and strips is a
    list of strips. A fan is also a list of triangle indices, and so
    is a strip.

    (Note: in the current implementation, fans is always [].)

    >>> triangles = [1, 5, 2, 5, 2, 6, 5, 9, 6, 9, 6, 10, 9, 13, 10, 13, 10, 14, 0, 4, 1, 4, 1, 5, 4, 8, 5, 8, 5, 9, 8, 12, 9, 12, 9, 13, 2, 6, 3, 6, 3, 7, 6, 10, 7, 10, 7, 11, 10, 14, 11, 14, 11, 15]
    >>> generateStrips(triangles)
    ([], [], [[1, 0, 1, 4, 5, 8, 9, 12, 13], [2, 1, 2, 5, 6, 9, 10, 13, 14], [3, 2, 3, 6, 7, 10, 11, 14, 15]])
    """

    # build a mesh from triangles
    mesh = Mesh()
    for face in _iterateTriangleList(triangles):
        mesh.AddFace(*face)

    # return the strip
    stripifier = Stripifier()
    stripifier(mesh)
    return stripifier.TriangleList, stripifier.TriangleFans, stripifier.TriangleStrips

if __name__=='__main__':
    import doctest
    doctest.testmod()
    
