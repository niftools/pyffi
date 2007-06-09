#!/usr/bin/env python

# http://techgame.net/projects/Runeblade/browser/trunk/RBRapier/RBRapier/Tools/Geometry/Analysis/TriangleStripifier.py?rev=760

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

from __future__ import generators
import TriangleMesh as Mesh

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _FindOtherFace(ev0, ev1, face):
    try:
        edge = face.GetEdge(ev0,ev1)
        # find a face with different edge windings
        result = edge.NextFace(face)
        if result:
            windings = face.GetVertexWinding(ev0,ev1), result.GetVertexWinding(ev0,ev1)
            while result and (windings[0] == windings[1]):
                result = edge.NextFace(result)
                if not result: return None
                if result == face: return None
                windings = face.GetVertexWinding(ev0,ev1), result.GetVertexWinding(ev0,ev1)
        return result
    except KeyError:
        return None

def _Counter():
    i = 1
    while 1:
        yield i
        i += 1

def _xwrap(idx, maxlen):
    while idx < maxlen:
        yield idx
        idx += 1
    maxlen,idx = idx,0
    while idx < maxlen:
        yield idx
        idx += 1

def _MakeSimpleMesh(mesh, data):
    i0, i1 = data[:2]
    for i2 in data[2:]:
        f = mesh.AddFace(i0, i1, i2)
        i0, i1 = i1, i2

def _ConjoinMeshData(*data):
    return [x for y in zip(*data) for x in y]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TriangleStrip(object):
    """
    Heavily adapted from NvTriStrip.
    Origional can be found at http://developer.nvidia.com/view.asp?IO=nvtristrip_library.
    """

    Faces = tuple()
    ExperimentId = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Public Methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, StartFace, StartEdge, StartForward=1, StripId=None, ExperimentId=None):
        # TODO: Can we combine StripID with pythonic ideas?
        self.StartFace = StartFace
        self.StartEdge = StartEdge
        if StartForward:
            v0,v1 = self.StartEdge.ev
        else: v1,v0 = self.StartEdge.ev
        self.StartEdgeOrder = v0, v1

        self.StripId = StripId or id(self)
        if ExperimentId is not None:
            self.ExperimentId = ExperimentId

    def __repr__(self):
        return "<FaceStrip |Faces|=%s>" % len(self.Faces)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Element Membership Tests
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def FaceInStrip(self, *faces):
        if self.ExperimentId is not None: key = 'TestStripId'
        else: key = 'StripId'
        for face in faces:
            if getattr(face, key, None) is self.StripId:
                return 1
        else: return 0

    def IsFaceMarked(self, face):
        result = getattr(face, 'StripId', None) is not None
        if not result and self.ExperimentId is not None:
            result = (getattr(face, 'ExperimentId', None) == self.ExperimentId)
        return result
    def MarkFace(self, face):
        if self.ExperimentId is not None:
            face.ExperimentId = self.ExperimentId
            face.TestStripId = self.StripId
        else:
            face.StripId = self.StripId
            try: del face.ExperimentId
            except AttributeError: pass
            try: del face.TestStripId
            except AttributeError: pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def Build(self):
        """Builds the face strip forwards, then backwards, and returns the joined list"""

        ForwardFaces = []
        self.Faces = BackwardFaces = []

        def _AlwaysTrue(face):
            """Utility for building face traversal list"""
            return 1

        def _UniqueFace(face):
            """Utility for building face traversal list"""
            v0,v1,v2=face.v
            bv0,bv1,bv2=0,0,0
            for faces in (ForwardFaces, BackwardFaces):
                for f in faces:
                    fv = f.v
                    if not bv0 and v0 in fv: bv0 = 1
                    if not bv1 and v1 in fv: bv1 = 1
                    if not bv2 and v2 in fv: bv2 = 1
                    if bv0 and bv1 and bv2: return 0
                else: return 1

        def _TraverseFaces(Indices, NextFace, FaceList, BreakTest):
            """Utility for building face traversal list"""
            #print "NEW TRAVERSAL"
            #print NextFace.v, Indices
            nv0,nv1 = Indices[-2:]
            NextFace = _FindOtherFace(nv0, nv1, NextFace)
            while NextFace and not self.IsFaceMarked(NextFace):
                if not BreakTest(NextFace): break
                nv0, nv1 = nv1, NextFace.OtherVertex(nv0, nv1)
                FaceList.append(NextFace)
                self.MarkFace(NextFace)
                Indices.append(nv1)
                #print NextFace.v, Indices
                NextFace = _FindOtherFace(nv0, nv1, NextFace)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        v0,v1 = self.StartEdgeOrder
        v2 = self.StartFace.OtherVertex(v0,v1)
        self.MarkFace(self.StartFace)
        ForwardFaces.append(self.StartFace)

        _TraverseFaces([v0,v1,v2], self.StartFace, ForwardFaces, _AlwaysTrue)
        _TraverseFaces([v2,v1,v0], self.StartFace, BackwardFaces, _UniqueFace)

        # Combine the Forward and Backward results
        BackwardFaces.reverse()
        self.StartFaceIndex = len(BackwardFaces)
        BackwardFaces.extend(ForwardFaces)
        self.Faces = BackwardFaces
        return self.Faces

    def Commit(self, TaskProgress=None):
        del self.ExperimentId
        count = len(map(self.MarkFace, self.Faces))
        if TaskProgress:
            TaskProgress += count
        return self

    def TriangleListIndices(self):
        result = []
        for face in self.Faces:
            result.extend(face.v)
        return result

    def TriangleStripIndices(self):
        FaceList = self.Faces
        FaceCount = len(FaceList)
        if FaceCount <= 0:
            # No faces is the easiest of all... return an empty list
            return []
        elif FaceCount == 1:
            # One face is really easy ;) just return the verticies in order
            return list(FaceList[0].v)
        elif FaceCount == 2:
            # The case of two faces is pretty simple too...
            face0,face1 = FaceList[:2]
            # Get the common edge
            edge01 = face0.GetCommonEdges(face1)[0]
            # Find the vertex on the first face not on the common edge
            result = [face0.OtherVertex(*edge01.ev)]
            # add the next two verticies on the edge in winding order
            result.append(face0.NextVertex(result[-1]))
            result.append(face0.NextVertex(result[-1]))
            # Find the vertex on the second face not on the common edge
            result.append(face1.OtherVertex(*edge01.ev))
            return result

        face0,face1,face2 = FaceList[:3]
        # Get the edge between face0 and face1
        edge01 = face0.GetCommonEdges(face1)[0]
        # Get the edge between face1 and face2
        edge12 = face1.GetCommonEdges(face2)[0]
        # Figure out which vertex we need to end on
        v2 = edge01.GetCommonVertices(edge12)[0]
        # Find the vertex on the first face not on the common edge
        v0 = face0.OtherVertex(*edge01.ev)
        # Find the middle vertex from the two endpoints
        v1 = face0.OtherVertex(v0, v2)

        # Figure out if the start triangle is backwards
        upsidedown = face0.NextVertex(v0) != v1
        if upsidedown:
            # We need to add a degenerate triangle to flip the strip over
            result = [v1,v0,v1,v2]
        else: result = [v0,v1,v2]

        for face in FaceList[1:]:
            # Build the strip by repeatedly finding the missing index
            result.append(face.OtherVertex(*result[-2:]))

        return result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ ExperimentGLSelector
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ExperimentGLSelector(object):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Constants / Variables / Etc.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Samples = 3
    StripLenHeuristic = 1.0
    MinStripLength = 3

    BestScore = None
    BestSample = None

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Definitions
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, Samples, MinStripLength):
        self.Samples = Samples
        self.MinStripLength = MinStripLength

    def Score(self, experiment):
        stripsize = 0
        for strip in experiment:
            stripsize += len(strip.Faces)
        score = self.StripLenHeuristic * stripsize / len(experiment)
        if score > self.BestScore:
            self.BestScore = score
            self.BestSample = experiment

    def Result(self):
        result = self.BestSample
        #print "SELECTED", self.BestScore, result
        del self.BestScore
        del self.BestSample
        return result

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ TriangleStripifier
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TriangleStripifier(object):
    """
    Heavily adapted from NvTriStrip.
    Origional can be found at http://developer.nvidia.com/view.asp?IO=nvtristrip_library.

    >>> mesh = Mesh.FaceEdgeMesh(); mesh.CleanFaces = 1
    >>> rows = [range(0,4), range(4,8), range(8,12), range(12,16)]
    >>> r0 = rows[0]
    >>> for r1 in rows[1:]:
    ...    _MakeSimpleMesh(mesh, _ConjoinMeshData(r0, r1)); r0=r1
    >>> mesh
    <FaceEdgeMesh |edges|=33 |faces|=18>
    >>> stripifier = TriangleStripifier()
    >>> r = stripifier.Stripify(mesh)
    >>> stripifier.TriangleList, stripifier.TriangleStrips
    ([], [[2, 1, 2, 5, 6, 9, 10, 13, 14], [1, 0, 1, 4, 5, 8, 9, 12, 13], [3, 2, 3, 6, 7, 10, 11, 14, 15]])
    >>> stripifier.GLSelector.MinStripLength = 100
    >>> r = stripifier.Stripify(mesh)
    >>> stripifier.TriangleList, stripifier.TriangleStrips
    ([1, 5, 2, 5, 2, 6, 5, 9, 6, 9, 6, 10, 9, 13, 10, 13, 10, 14, 0, 4, 1, 4, 1, 5, 4, 8, 5, 8, 5, 9, 8, 12, 9, 12, 9, 13, 2, 6, 3, 6, 3, 7, 6, 10, 7, 10, 7, 11, 10, 14, 11, 14, 11, 15], [])
    >>> del stripifier.GLSelector.MinStripLength
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Constants / Variables / Etc.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    GLSelector = ExperimentGLSelector(3, 3)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Public Methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def Stripify(self, mesh, TaskProgress=None):
        self.TriangleList = []
        self.TriangleStrips = []
        #self.TriangleFans = []

        # TODO: Could find triangle fans here
        Strips = self._FindAllStrips(mesh, TaskProgress)
        for strip in Strips:
            if len(strip.Faces) < self.GLSelector.MinStripLength:
                self.TriangleList.extend(strip.TriangleListIndices())
            else:
                self.TriangleStrips.append(strip.TriangleStripIndices())

        result = [('list', self.TriangleList), ('strip', self.TriangleStrips)]#, ('fan',self.TriangleFans) ]
        return result
       
    __call__ = Stripify

    def StripifyIter(self, mesh, TaskProgress=None):
        # TODO: Could find triangle fans here
        Strips = self._FindAllStrips(mesh, TaskProgress)
        for strip in Strips:
            if len(strip.Faces) < self.GLSelector.MinStripLength:
               yield 'list', strip.TriangleListIndices()
            else:
               yield 'strip', strip.TriangleStripIndices()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #~ Protected Methods
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _FindStartFaceIndex(self, FaceList):
        """Find a good face to start stripification with."""
        bestfaceindex, bestscore = 0, None
        faceindex = -1

        for face in FaceList:
            faceindex  += 1
            score = 0
            for edge in face.edges:
                score += not edge.NextFace(face) and 1 or 0
            # best possible score is 2 -- a face with only one neighbor
            # (a score of 3 signifies a lonely face)
            if bestscore < score < 3:
                bestfaceindex, bestscore = faceindex, score
                if bestscore >= 2: break
        return bestfaceindex

    def _FindGoodResetPoint(self, mesh):
        FaceList = mesh.Faces
        lenFaceList = len(mesh.Faces)
        startstep = lenFaceList / 10
        startidx = self._FindStartFaceIndex(FaceList)
        while startidx is not None:
            for idx in _xwrap(startidx, lenFaceList):
                face = FaceList[idx]
                # If this face isn't used by another strip
                if getattr(face, 'StripId', None) is None:
                    startidx = idx + startstep
                    while startidx >= lenFaceList:
                        startidx -= lenFaceList
                    yield face
                    break
            else:
                # We've exhausted all the faces... so lets exit this loop
                break

    def _FindTraversal(self, strip):
        mesh = strip.StartFace.mesh
        FaceList = strip.Faces
        def _IsItHere(idx, currentedge):
            face = FaceList[idx]
            # Get the next vertex in this strips' walk
            v2 = face.OtherVertex(*currentedge)
            # Find the edge parallel to the strip, namely v0 to v2
            paralleledge = mesh.GetEdge(currentedge[0], v2)
            # Find the other face off the parallel edge
            otherface = paralleledge.NextFace(face)
            if otherface and not strip.FaceInStrip(otherface) and not strip.IsFaceMarked(otherface):
                # If we can use it, then do it!
                otheredge = mesh.GetEdge(currentedge[0], otherface.OtherVertex(*paralleledge.ev))
                # TODO: See if we are getting the proper windings.  Otherwise toy with the following
                return otherface, otheredge, (otheredge.ev[0] == currentedge[0]) and 1 or 0
            else:
                # Keep looking...
                currentedge[:] = [currentedge[1], v2]

        startindex = strip.StartFaceIndex
        currentedge = list(strip.StartEdgeOrder[:])
        for idx in xrange(startindex, len(FaceList), 1):
            result = _IsItHere(idx, currentedge)
            if result is not None: return result

        currentedge = list(strip.StartEdgeOrder[:])
        currentedge.reverse()
        for idx in xrange(startindex-1, -1, -1):
            result = _IsItHere(idx, currentedge)
            if result is not None: return result

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _FindAllStrips(self, mesh, TaskProgress=None):
        selector = self.GLSelector
        bCleanFaces = getattr(mesh, 'CleanFaces', 0)
        GoodResetPoints = self._FindGoodResetPoint(mesh)
        experimentId = _Counter()
        stripId = _Counter()

        StripifyTask = 0
        CleanFacesTask = 0
        if TaskProgress:
            StripifyTask = TaskProgress.NewSubtask("Triangle mesh stripification", 0, len(mesh.Faces))
            if bCleanFaces:
                CleanFacesTask = TaskProgress.NewSubtask("Clean faces", 0, len(mesh.Faces))

        try:
            while 1:
                Experiments = []
                ResetPoints = {}
                VisitedResetPoints = {}
               
                for nSample in xrange(selector.Samples):
                    # Get a good start face for an experiment
                    ExpFace = GoodResetPoints.next()
                    if ExpFace in VisitedResetPoints:
                        # We've seen this face already... try again
                        continue
                    VisitedResetPoints[ExpFace] = 1

                    # Create an exploration from ExpFace in each of the three edge directions
                    for ExpEdge in ExpFace.edges:
                        # See if the edge is pointing in the direction we expect
                        flag = ExpFace.GetVertexWinding(*ExpEdge.ev)
                        # Create the seed strip for the experiment
                        siSeed = TriangleStrip(ExpFace, ExpEdge, flag, stripId.next(), experimentId.next())
                        # Add the seeded experiment list to the experiment collection
                        Experiments.append([siSeed])

                while Experiments:
                    exp = Experiments.pop()
                    while 1:
                        # Build the the last face of the experiment
                        exp[-1].Build()
                        # See if there is a connecting face that we can move to
                        traversal = self._FindTraversal(exp[-1])
                        if traversal:
                            # if so, add it to the list
                            traversal += (stripId.next(), exp[0].ExperimentId)
                            exp.append(TriangleStrip(*traversal))
                        else:
                            # Otherwise, we're done
                            break
                    selector.Score(exp)

                # Get the best experiment according to the selector
                BestExperiment = selector.Result()
                # And commit it to the resultset
                for each in BestExperiment:
                    yield each.Commit(StripifyTask)
                del BestExperiment
        except StopIteration:
            pass

        if bCleanFaces:
            for face in mesh.Faces:
                try: del face.StripId
                except AttributeError: pass
                CleanFacesTask += 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PrintOnProgress(object):
    percent = 0.
    def __init__(self, printline=1, stepcount=20):
        import sys
        self.out = sys.stdout
        self.printline = printline
        self.out.write("<")
        self.step = 1./stepcount
    def __del__(self):
        import os
        self.out.write(">")
        if self.printline:
            self.out.write(os.linesep)
    def __call__(self, percent):
        while percent - self.percent >= self.step:
            self.out.write("*")
            self.percent += self.step

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Optimization
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

try: import psyco
except ImportError: pass
else:
    psyco.bind(TriangleStrip)
    psyco.bind(ExperimentGLSelector)
    psyco.bind(TriangleStripifier)
    psyco.bind(_FindOtherFace)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Testing
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    print "Testing..."
    import time
    import doctest
    import TriangleStripifier as _testmod
    doctest.testmod(_testmod)

    rowcount,colcount = 26,26
    rows = []
    for ri in xrange(rowcount):
        rows.append(range(ri*colcount, (ri+1)*colcount))

    startmesh = time.clock()
    mesh = Mesh.FaceEdgeMesh()
    r0 = rows[0]
    for r1 in rows[1:]:
        _MakeSimpleMesh(mesh, _ConjoinMeshData(r0, r1)); r0=r1
    print mesh
    donemesh = time.clock()
    print "Meshed:", donemesh, donemesh - startmesh

    startstrip = time.clock()
    stripifier = TriangleStripifier()
    stripifier(mesh, OnProgress=PrintOnProgress())
    donestrip = time.clock()
    print "Stripped", donestrip, donestrip-startstrip

    print "Test complete."
