from TraversalUtilities import Stripifier
from Mesh import Mesh

def triangulate(strips):
    """A generator for iterating over the faces in a set of
    strips. Degenerate triangles in strips are discarded.

    >>> triangulate([[1, 0, 1, 2, 3, 4, 5, 6]])
    [[0, 2, 1], [1, 2, 3], [2, 4, 3], [3, 4, 5], [4, 6, 5]]
    """

    triangles = []

    for strip in strips:
        i = strip.__iter__()
        j = True
        t1, t2 = i.next(), i.next()
        for k in xrange(2, len(strip)):
            t0, t1, t2 = t1, t2, i.next()
            if t0 == t1 or t1 == t2 or t2 == t0:
                j = not j
                continue
            triangles.append([t0, t1, t2] if j else [t0, t2, t1])
            j = not j

    return triangles

def _generateFacesFromTriangles(triangles):
    i = triangles.__iter__()
    while True:
        yield [i.next(), i.next(), i.next()]

def strippify(faces):
    """Converts faces into a list of strips.

    >>> faces = [[1, 5, 2], [5, 2, 6], [5, 9, 6], [9, 6, 10], [9, 13, 10], [13, 10, 14], [0, 4, 1], [4, 1, 5], [4, 8, 5], [8, 5, 9], [8, 12, 9], [12, 9, 13], [2, 6, 3], [6, 3, 7], [6, 10, 7], [10, 7, 11], [10, 14, 11], [14, 11, 15]]
    >>> strippify(faces)
    [[1, 0, 1, 4, 5, 8, 9, 12, 13], [2, 1, 2, 5, 6, 9, 10, 13, 14], [3, 2, 3, 6, 7, 10, 11, 14, 15]]
    >>> strippify([[0,1,4],[1,2,4],[2,3,4],[3,0,4]])
    [[3, 0, 4, 1, 2], [2, 3, 4]]
    >>> strippify([[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23]])
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 13, 14], [15, 16, 17], [18, 19, 20], [21, 22, 23]]
    >>> strippify([[0, 1, 2], [0, 1, 2]])
    [[0, 1, 2], [0, 1, 2]]
    >>> strippify([[0, 1, 2], [2, 1, 0]])
    [[0, 1, 2, 0]]
    >>> strippify([[0, 1, 2], [0, 2, 3], [4, 0, 3], [0, 4, 3]])
    None
    """

    # build a mesh from triangles
    mesh = Mesh()
    for face in faces:
        mesh.AddFace(*face)

    # calculate the strip
    stripifier = Stripifier()
    stripifier.Selector.MinStripLength = 0
    stripifier(mesh)

    # add the triangles to it
    i = stripifier.TriangleList.__iter__()
    return [face for face in _generateFacesFromTriangles(stripifier.TriangleList)] + stripifier.TriangleStrips

if __name__=='__main__':
    import doctest
    doctest.testmod()
    
