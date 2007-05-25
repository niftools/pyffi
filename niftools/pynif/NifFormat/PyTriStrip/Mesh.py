#!/usr/bin/env python
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
#~ Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import weakref

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FlyweightGroupObject(object):
    def ClassFlyweightGroup(klass, name, **kw):
        return type(name, (klass,), kw)
    ClassFlyweightGroup = classmethod(ClassFlyweightGroup)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Edge(FlyweightGroupObject):
    def __init__(self, ev0, ev1):
        self.ev = (ev0, ev1)
        self.Faces = []

    def __hash__(self):
        return hash(self.ev)

    def __repr__(self):
        return "<%s ev=%s>" % (self.__class__.__name__, self.ev)

    def GetCommonVertices(self, otheredge):
        return [v for v in otheredge.ev if v in self.ev]

    def NextFace(self, face=None):
        if face is None: idx = 0
        else: idx = self.Faces.index(face)
        result = self.Faces[idx-1]
        if result == face: result = None
        return result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Face(FlyweightGroupObject):
    def __init__(self, v0,v1,v2):
        self.v = (v0,v1,v2)
    def __eq__(self, other):
        return self.v == other.v
    def __ne__(self, other):
        return self.v != other.v

    def __hash__(self):
        return hash(self.v)

    def __repr__(self):
        return "<%s v=%s>" % (self.__class__.__name__, self.v)

    _VertexWindingTable = {1:0, -1:1, -2:0, 2:1}
    # 1 corresponds to e01 or e12
    # -1 corresponds to e10 = -e01; or e12 = -e21
    # 2 corresponds to e20
    # -2 corresponds to e02 = -e20

    def GetVertexWinding(self, pv0, pv1):
        v = list(self.v)
        delta = v.index(pv1) - v.index(pv0)
        return self._VertexWindingTable[delta]

    def NextVertex(self, vi):
        idx = list(self.v).index(vi) + 1
        if idx >= len(self.v):
            return self.v[0]
        else: return self.v[idx]

    def OtherVertex(self, pv0, pv1):
        result = [v for v in self.v if v!=pv0 and v!=pv1]
        if len(result) == 1:
            return result[0]
        elif len(result) > 1:
            raise KeyError, "Expected one vertex, but found many! (%r, %r, %r)" % (self.v, (pv0, pv1), result)
        else:
                raise KeyError, "Expected one vertex, but found none! (%r, %r, %r)" % (self.v, (pv0, pv1), result)
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class EdgedFace(Face):
    def __init__(self, v0,v1,v2):
        Face.__init__(self, v0,v1,v2)
        e01 = self.mesh.AddEdge(v0,v1, weakref.proxy(self))
        e12 = self.mesh.AddEdge(v1,v2, weakref.proxy(self))
        e20 = self.mesh.AddEdge(v2,v0, weakref.proxy(self))
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

class Mesh(FlyweightGroupObject):
    """
    >>> mesh = Mesh(); mesh
    <Mesh |edges|=0 |faces|=0>
    >>> i0, i1 = 0, 1
    >>> for i2 in xrange(2, 8):
    ...     f = mesh.AddFace(i0, i1, i2)
    ...     i0, i1 = i1, i2
    >>> mesh
    <Mesh |edges|=13 |faces|=6>
    >>> face = mesh.Faces[0]; face
    <Mesh&EdgedFace v=(0, 1, 2)>
    >>> face.OtherVertex(0,1)
    2
    >>> face.GetEdge(2,1)
    <Mesh&Edge ev=(1, 2)>
    """

    def __init__(self, FaceClass=EdgedFace, EdgeClass=Edge):
        FaceClassName = '%s&%s'%(self.__class__.__name__, FaceClass.__name__)
        self._FaceClass = FaceClass.ClassFlyweightGroup(FaceClassName , mesh=weakref.proxy(self))
        self.Faces = []

        EdgeClassName = '%s&%s'%(self.__class__.__name__, EdgeClass.__name__)
        self._EdgeClass = EdgeClass.ClassFlyweightGroup(EdgeClassName , mesh=weakref.proxy(self))
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
            edge = self._EdgeClass(ev0,ev1)
            self.Edges[ev0,ev1] = edge

        edge.Faces.append(face)
        #if len(edge.Faces) > 2:
        #    print "ABNORMAL Edge:", edge, edge.Faces
        return edge

    def AddFace(self, v0,v1,v2):
        if v0 == v1 or v1 == v2 or v2 == v0:
            #print "DEGENERATE face", (v0,v1,v2)
            return None
        else:
            face = self._FaceClass(v0,v1,v2)
            self.Faces.append(face)
            return face

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Testing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    print "Testing..."
    import doctest
    import Mesh as _testmod
    doctest.testmod(_testmod)
    print "Test complete."

