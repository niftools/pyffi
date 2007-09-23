#!/usr/bin/env python

# http://techgame.net/projects/Runeblade/browser/trunk/RBRapier/RBRapier/Tools/Geometry/Analysis/TriangleMesh.py?rev=760

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##~ License
##~
##- The RuneBlade Foundation library is intended to ease some
##- aspects of writing intricate Jabber, XML, and User Interface (wxPython, etc.)
##- applications, while providing the flexibility to modularly change the
##- architecture. Enjoy.
##~
##~ Copyright (C) 2002  TechGame Networks, LLC.
##~
##~ This library is free software; you can redistribute it and/or
##~ modify it under the terms of the BSD style License as found in the
##~ LICENSE file included with this distribution.
##~
##~ TechGame Networks, LLC can be reached at:
##~ 3578 E. Hartsel Drive #211
##~ Colorado Springs, Colorado, USA, 80920
##~
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

cdef class Edge:
    cdef int ev[2]

    def __init__(self, int ev0, int ev1):
        self.ev[0] = ev0
        self.ev[1] = ev1
        self.Faces = []

    def GetCommonVertices(self, Edge otheredge):
        result = []
        if self.v[0] == otheredge.v[0]: result.append(self.v[0])
        if self.v[1] == otheredge.v[1]: result.append(self.v[1])
        if self.v[1] == otheredge.v[0]: result.append(self.v[1])
        if self.v[0] == otheredge.v[1]: result.append(self.v[0])
        return result

    def NextFace(self, face=None):
        if face is None: idx = 0
        else: idx = self.Faces.index(face)
        result = self.Faces[idx-1]
        if result == face: result = None
        return result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

cdef class Face:
    cdef int v[3]

    def __init__(self, int v0, int v1, int v2):
        self.v[0] = v0
        self.v[1] = v1
        self.v[2] = v2
    def __richcmp__(self, other, int op):
        cdef int i

        if op == 2 or op == 3:
            if self.v[0] == other.v[0] and self.v[1] == other.v[1] and self.v[2] == other.v[2]: return op == 2
            return op == 3
        elif op == 0 or op == 1:
            if self.v[0] < other.v[0]: return True
            if self.v[0] > other.v[0]: return False
            if self.v[1] < other.v[1]: return True
            if self.v[1] > other.v[1]: return False
            if op == 0:
                return self.v[2] < other.v[2]
            else:
                return self.v[2] <= other.v[2]
        elif op == 4 or op == 5:
            if self.v[0] < other.v[0]: return False
            if self.v[0] > other.v[0]: return True
            if self.v[1] < other.v[1]: return False
            if self.v[1] > other.v[1]: return True
            if op == 4:
                return self.v[2] > other.v[2]
            else:
                return self.v[2] >= other.v[2]

    #_VertexWindingTable = {1:0, -1:1, -2:0, 2:1}
    # 1 corresponds to e01 or e12
    # -1 corresponds to e10 = -e01; or e12 = -e21
    # 2 corresponds to e20
    # -2 corresponds to e02 = -e20

    def Index(self, int v):
        if v == self.v[0]: return 0
        if v == self.v[1]: return 1
        if v == self.v[2]: return 2
        raise IndexError

    def GetVertexWinding(self, int pv0, int pv1):
        #v = list(self.v)
        cdef int delta
        delta = self.Index(pv1) - self.Index(pv0)
        if delta == 1 or delta == -2: return 0
        else: return 1

    def NextVertex(self, int vi):
        cdef int idx
        idx = self.Index(vi) + 1
        if idx >= 3:
            return self.v[0]
        else: return self.v[idx]

    def OtherVertex(self, int pv0, int pv1):
        if self.v[0] != pv0 and self.v[0] != pv1: return self.v[0]
        if self.v[1] != pv0 and self.v[1] != pv1: return self.v[1]
        return self.v[2]
        #if v[2] != pv0 and v[2] != pv1: return v[2]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class EdgedFace(Face):
    def __init__(self, v0,v1,v2):
        Face.__init__(self, v0,v1,v2)
        e01 = self.mesh.AddEdge(v0,v1)
        e12 = self.mesh.AddEdge(v1,v2)
        e20 = self.mesh.AddEdge(v2,v0)
        self.edges = [e01, e12, e20]

    def GetEdge(self, ev0, ev1):
        assert ev0 != ev1
        v = list(self.v)
        idx0,idx1 = v.index(ev0), v.index(ev1)
        if idx0 > idx1: idx0,idx1 = idx1,idx0
        if idx0 == 0:
            if idx1==2: return self.edges[2]
            else: return self.edges[0]
        else: return self.edges[1]

    def GetCommonEdges(self, otherface):
        return [edge for edge in otherface.edges if edge in self.edges]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FaceMesh:
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Constants / Variables / Etc.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    WarnOnOddities = 0

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Public Methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self):
        #FaceClassName = '%s&%s'%(self.__class__.__name__, FaceClass.__name__)
        #self._FaceClass = FaceClass.ClassFlyweightGroup(FaceClassName, mesh=weakref.proxy(self))
        self.Faces = []

    def __repr__(self):
        return "<%s |faces|=%s>" % (self.__class__.__name__, len(self.Faces))

    def AddFace(self, v0,v1,v2):
        if v0 == v1 or v1 == v2 or v2 == v0:
            if self.WarnOnOddities:
                print "DEGENERATE face", (v0,v1,v2)
            return None
        else:
            face = Face(v0,v1,v2)
            self.Faces.append(face)
            return face

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FaceEdgeMesh:
    """
    >>> mesh = FaceEdgeMesh(); mesh
    <FaceEdgeMesh |edges|=0 |faces|=0>
    >>> i0, i1 = 0, 1
    >>> for i2 in xrange(2, 8):
    ...     f = mesh.AddFace(i0, i1, i2)
    ...     i0, i1 = i1, i2
    >>> mesh
    <FaceEdgeMesh |edges|=13 |faces|=6>
    >>> face = mesh.Faces[0]; face
    <FaceEdgeMesh&EdgedFace v=(0, 1, 2)>
    >>> face.OtherVertex(0,1)
    2
    >>> face.GetEdge(2,1)
    <FaceEdgeMesh&Edge ev=(1, 2)>
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Constants / Variables / Etc.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    WarnOnOddities = 0

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Public Methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self):
        #FaceClassName = '%s&%s'%(self.__class__.__name__, FaceClass.__name__)
        #self._FaceClass = FaceClass.ClassFlyweightGroup(FaceClassName , mesh=weakref.proxy(self))
        self.Faces = []

        #EdgeClassName = '%s&%s'%(self.__class__.__name__, EdgeClass.__name__)
        #self._EdgeClass = EdgeClass.ClassFlyweightGroup(EdgeClassName , mesh=weakref.proxy(self))
        self.Edges = {}

    def __repr__(self):
        return "<%s |edges|=%s |faces|=%s>" % (self.__class__.__name__, len(self.Edges), len(self.Faces))

    def HasEdge(self, ev0, ev1):
        if ev0 > ev1: ev1,ev0=ev0,ev1
        return (ev0,ev1) in self.Edges
    def GetEdge(self, ev0, ev1):
        if ev0 > ev1: ev1,ev0=ev0,ev1
        return self.Edges[ev0,ev1]

    def AddEdge(self, ev0, ev1, face):
        if ev0 > ev1: ev1,ev0=ev0,ev1
        try:
            edge = self.Edges[ev0,ev1]
        except KeyError:
            edge = Edge(ev0,ev1)
            self.Edges[ev0,ev1] = edge

        edge.Faces.append(face)
        if self.WarnOnOddities:
            if len(edge.Faces) > 2:
                print "ABNORMAL Edge:", edge, edge.Faces
        return edge

    def AddFace(self, v0,v1,v2):
        if v0 == v1 or v1 == v2 or v2 == v0:
            if self.WarnOnOddities:
                print "DEGENERATE face", (v0,v1,v2)
            return None
        else:
            face = EdgedFace(v0,v1,v2)
            self.Faces.append(face)
            return face

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Optimization
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

try: import psyco
except ImportError: pass
else:
    psyco.bind(Edge)
    psyco.bind(Face)
    psyco.bind(EdgedFace)
    psyco.bind(FaceMesh)
    psyco.bind(FaceEdgeMesh)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Testing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    print "Testing..."
    import doctest
    import TriangleMesh as _testmod
    doctest.testmod(_testmod)
    print "Test complete."

