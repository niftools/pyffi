"""A general purpose stripifier, based on NvTriStrip (http://developer.nvidia.com/)

Credit for porting NvTriStrip to Python goes to the RuneBlade Foundation
library:
http://techgame.net/projects/Runeblade/browser/trunk/RBRapier/RBRapier/Tools/Geometry/Analysis/TriangleStripifier.py?rev=760

The algorithm of this stripifier is an improved version of the RuneBlade
Foundation / NVidia stripifier; it makes no assumptions about the
underlying geometry whatsoever and is intended to produce valid
output in all circumstances.
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import itertools
import sys
import weakref

from pyffi.utils.trianglemesh import Face, Mesh

class TriangleStrip(object):
    """
    Heavily adapted from NvTriStrip.
    Origional can be found at http://developer.nvidia.com/view.asp?IO=nvtristrip_library.
    """

    def __init__(self, experiment=None,
                 faces=None, vertices=None, reversed_=False):
        """Initialise the triangle strip."""
        self.faces = faces if faces else []
        self.vertices = vertices if vertices else []
        self.reversed_ = reversed_
        self.experiment = weakref.proxy(experiment)

    def __repr__(self):
        return ("TriangleStrip(faces=%s, vertices=%s, reversed_=%s)"
                % (repr(self.faces), repr(self.vertices), repr(self.reversed_)))

    def get_unstripped_adjacent_face(self, face, vi):
        """Get adjacent face which is not yet stripped."""
        for otherface in face.get_adjacent_faces(vi):
            if self.experiment.is_unstripped(otherface.index):
                return otherface

    def traverse_faces(self, start_vertex, start_face, forward):
        """Building face traversal list starting from the start_face and
        the edge opposite start_vertex. Returns number of faces added.
        """
        count = 0
        pv0 = start_vertex
        pv1 = start_face.get_next_vertex(pv0)
        pv2 = start_face.get_next_vertex(pv1)
        next_face = self.get_unstripped_adjacent_face(start_face, pv0)
        while next_face:
            self.experiment.stripped_faces.add(next_face.index)
            count += 1
            if count & 1:
                if forward:
                    pv0 = pv1
                    pv1 = next_face.get_next_vertex(pv0)
                    self.vertices.append(pv1)
                    self.faces.append(next_face)
                else:
                    pv0 = pv2
                    pv2 = next_face.get_next_vertex(pv1)
                    self.vertices.insert(0, pv2)
                    self.faces.insert(0, next_face)
                    self.reversed_ = not self.reversed_
            else:
                if forward:
                    pv0 = pv2
                    pv2 = next_face.get_next_vertex(pv1)
                    self.vertices.append(pv2)
                    self.faces.append(next_face)
                else:
                    pv0 = pv1
                    pv1 = next_face.get_next_vertex(pv0)
                    self.vertices.insert(0, pv1)
                    self.faces.insert(0, next_face)
                    self.reversed_ = not self.reversed_
            next_face = self.get_unstripped_adjacent_face(next_face, pv0)
        return count

    def build(self, start_vertex, start_face):
        """Builds the face strip forwards, then backwards. Returns
        index of start_face.

        Check case of single triangle
        -----------------------------

        >>> m = Mesh()
        >>> face = m.add_face(0, 1, 2)
        >>> m.lock()
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(0, face)
        0
        >>> t
        TriangleStrip(faces=[Face(0, 1, 2)], vertices=[0, 1, 2], reversed_=False)
        >>> t.get_strip()
        [0, 1, 2]
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(1, face)
        0
        >>> t
        TriangleStrip(faces=[Face(0, 1, 2)], vertices=[1, 2, 0], reversed_=False)
        >>> t.get_strip()
        [1, 2, 0]
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(2, face)
        0
        >>> t
        TriangleStrip(faces=[Face(0, 1, 2)], vertices=[2, 0, 1], reversed_=False)
        >>> t.get_strip()
        [2, 0, 1]

        Check case of two triangles, with special strip winding fix
        -----------------------------------------------------------

        >>> m = Mesh()
        >>> face0 = m.add_face(0, 1, 2)
        >>> face1 = m.add_face(2, 1, 3)
        >>> m.lock()
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(0, face0)
        0
        >>> t
        TriangleStrip(faces=[Face(0, 1, 2), Face(1, 3, 2)], vertices=[0, 1, 2, 3], reversed_=False)
        >>> t.get_strip()
        [0, 1, 2, 3]
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(1, face0)
        1
        >>> t
        TriangleStrip(faces=[Face(1, 3, 2), Face(0, 1, 2)], vertices=[3, 1, 2, 0], reversed_=True)
        >>> t.get_strip()
        [3, 2, 1, 0]
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(2, face1)
        1
        >>> t
        TriangleStrip(faces=[Face(0, 1, 2), Face(1, 3, 2)], vertices=[0, 2, 1, 3], reversed_=True)
        >>> t.get_strip()
        [0, 1, 2, 3]
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(3, face1)
        0
        >>> t
        TriangleStrip(faces=[Face(1, 3, 2), Face(0, 1, 2)], vertices=[3, 2, 1, 0], reversed_=False)
        >>> t.get_strip()
        [3, 2, 1, 0]

        Check that extra vertex is appended to fix winding
        --------------------------------------------------

        >>> m = Mesh()
        >>> face0 = m.add_face(1, 3, 2)
        >>> face1 = m.add_face(2, 3, 4)
        >>> face2 = m.add_face(4, 3, 5)
        >>> face3 = m.add_face(4, 5, 6)
        >>> m.lock()
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(2, face1)
        1
        >>> t
        TriangleStrip(faces=[Face(1, 3, 2), Face(2, 3, 4), Face(3, 5, 4), Face(4, 5, 6)], vertices=[1, 2, 3, 4, 5, 6], reversed_=True)
        >>> t.get_strip()
        [1, 1, 2, 3, 4, 5, 6]

        Check that strip is reversed to fix winding
        -------------------------------------------

        >>> m = Mesh()
        >>> face0 = m.add_face(1, 3, 2)
        >>> face1 = m.add_face(2, 3, 4)
        >>> face2 = m.add_face(4, 3, 5)
        >>> m.lock()
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(2, face1)
        1
        >>> t
        TriangleStrip(faces=[Face(1, 3, 2), Face(2, 3, 4), Face(3, 5, 4)], vertices=[1, 2, 3, 4, 5], reversed_=True)
        >>> t.get_strip()
        [5, 4, 3, 2, 1]

        More complicated mesh
        ---------------------

        >>> m = Mesh()
        >>> face0 = m.add_face(0, 1, 2)
        >>> face1 = m.add_face(2, 1, 7)
        >>> face2 = m.add_face(2, 7, 4)
        >>> face3 = m.add_face(5, 3, 2)
        >>> face4 = m.add_face(2, 1, 9)
        >>> face5 = m.add_face(4, 7, 10)
        >>> face6 = m.add_face(4, 10, 11)
        >>> face7 = m.add_face(11, 10, 12)
        >>> face8 = m.add_face(1, 0, 13)
        >>> m.lock()
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(7, face1)
        4
        >>> t.faces[4] == face1 # check result from build
        True
        >>> t.experiment.stripped_faces
        set([0, 1, 2, 5, 6, 7, 8])
        >>> t.faces
        [Face(10, 12, 11), Face(4, 10, 11), Face(4, 7, 10), Face(2, 7, 4), Face(1, 7, 2), Face(0, 1, 2), Face(0, 13, 1)]
        >>> t.vertices
        [12, 11, 10, 4, 7, 2, 1, 0, 13]
        >>> t.reversed_
        False
        >>> t.get_strip()
        [12, 11, 10, 4, 7, 2, 1, 0, 13]

        Mesh which has more than a single strip
        ---------------------------------------

        >>> m = Mesh()
        >>> tmp = m.add_face(2, 1, 7) # in strip
        >>> start_face = m.add_face(0, 1, 2) # in strip
        >>> tmp = m.add_face(2, 7, 4) # in strip
        >>> tmp = m.add_face(4, 7, 11) # in strip
        >>> tmp = m.add_face(5, 3, 2)
        >>> tmp = m.add_face(1, 0, 8) # in strip
        >>> tmp = m.add_face(0, 8, 9) # bad orientation!
        >>> tmp = m.add_face(8, 0, 10) # in strip
        >>> m.lock()
        >>> exp = Experiment(m)
        >>> t = TriangleStrip(exp)
        >>> t.build(0, start_face)
        2
        >>> t.vertices
        [10, 8, 0, 1, 2, 7, 4, 11]
        >>> t.get_strip()
        [10, 8, 0, 1, 2, 7, 4, 11]
        """
        del self.faces[:]
        del self.vertices[:]
        self.reversed_ = False
        v0 = start_vertex
        v1 = start_face.get_next_vertex(v0)
        v2 = start_face.get_next_vertex(v1)
        self.experiment.stripped_faces.add(start_face.index)
        self.faces.append(start_face)
        self.vertices.append(v0)
        self.vertices.append(v1)
        self.vertices.append(v2)
        self.traverse_faces(v0, start_face, True)
        return self.traverse_faces(v2, start_face, False)

    def get_strip(self):
        """Get strip in forward winding."""
        strip = []
        if self.reversed_:
            if len(self.vertices) & 1:
                strip = list(reversed(self.vertices))
            elif len(self.vertices) == 4:
                strip = list(self.vertices[i] for i in (0, 2, 1, 3))
            else:
                strip = list(self.vertices)
                strip.insert(0, strip[0])
        else:
            strip = list(self.vertices)
        return strip

class Experiment(object):
    num_samples = 10
    recursion_depth = 1

    def __init__(self, mesh, start_vertex=None, start_face=None, parent=None):
        self.mesh = mesh
        self.start_vertex = start_vertex
        self.start_face = start_face
        if parent:
            self.parent = weakref.proxy(parent)
            self.level = parent.level + 1
        else:
            self.parent = None # root object!
            self.level = 0
        self.stripped_faces = set() # faces stripped in this experiment
        self.strips = [] # strips in this experiment

        # other experiments which build further on this experiment
        self.children = []

    def is_unstripped(self, face_index):
        """Find out if a face index is part of current experiment or not."""
        if face_index in self.stripped_faces:
            return False
        elif self.parent:
            return self.parent.is_unstripped(face_index)
        return True

    def get_all_stripped_faces(self):
        """Use this if you need to call is_unstripped a lot."""
        if not self.parent:
            return self.stripped_faces
        else:
            return self.stripped_faces | self.parent.get_all_stripped_faces()

    def build(self):
        """Build strips, starting from start_vertex and start_face.

        >>> m = Mesh()
        >>> tmp = m.add_face(2, 1, 7)
        >>> s1_face = m.add_face(0, 1, 2)
        >>> tmp = m.add_face(2, 7, 4) # in strip
        >>> tmp = m.add_face(4, 7, 11) # in strip
        >>> tmp = m.add_face(5, 3, 2)
        >>> tmp = m.add_face(1, 0, 8) # in strip
        >>> tmp = m.add_face(0, 8, 9) # bad orientation!
        >>> tmp = m.add_face(8, 0, 10) # in strip
        >>> tmp = m.add_face(10, 11, 8) # in strip
        >>> # parallel strip
        >>> s2_face = m.add_face(0, 2, 21) # in strip
        >>> tmp = m.add_face(21, 2, 22) # in strip
        >>> tmp = m.add_face(2, 4, 22) # in strip
        >>> tmp = m.add_face(21, 24, 0) # in strip
        >>> tmp = m.add_face(9, 0, 24) # in strip
        >>> # parallel strip, further down
        >>> s3_face = m.add_face(8, 11, 31) # in strip
        >>> tmp = m.add_face(8, 31, 32) # in strip
        >>> tmp = m.add_face(31, 11, 33) # in strip
        >>> m.lock()
        >>> # build experiment
        >>> root = parent=Experiment(m)
        >>> exp = Experiment(m, 0, s1_face, parent=root)
        >>> exp.recursion_depth = 0 # just do a single experiment
        >>> exp.build() # not yet finished?
        False
        >>> exp.score() # average strip length is (7+5)/2 = 6
        6.0
        >>> len(exp.strips)
        2
        >>> exp.strips[0].get_strip()
        [11, 4, 7, 2, 1, 0, 8, 10, 11]
        >>> exp.strips[1].get_strip()
        [4, 22, 2, 21, 0, 24, 9]
        >>> # not found with current algorithm
        >>> #exp.strips[2].get_strip()
        >>> #[32, 8, 31, 11, 33]
        """
        # build initial strip if this is not the root node
        if self.parent:
            strip = TriangleStrip(experiment=self)
            strip.build(self.start_vertex, self.start_face)
            self.strips.append(strip)
            # build adjacent strips
            num_faces = len(strip.faces)
            if num_faces >= 4:
                self.build_adjacent(strip, num_faces / 2)
                self.build_adjacent(strip, num_faces / 2 + 1)
            elif num_faces == 3:
                if not self.build_adjacent(strip, 0):
                    self.build_adjacent(strip, 2)
                self.build_adjacent(strip, 1)
            elif num_faces == 2:
                self.build_adjacent(strip, 0)
                self.build_adjacent(strip, 1)
            elif num_faces == 1:
                self.build_adjacent(strip, 0)

        # create child experiments if recursion depth not reached
        if self.level < self.recursion_depth:
            for face_index in self.find_good_reset_points():
                exp_face = self.mesh.faces[face_index]
                for exp_vertex in exp_face.verts:
                    self.children.append(
                        Experiment(
                            self.mesh,
                            start_vertex=exp_vertex,
                            start_face=exp_face,
                            parent=self))
            # build them
            for child in self.children:
                child.build()

        # we have built something, if there are children
        return bool(self.children)

    def build_adjacent(self, strip, face_index):
        """Build strips adjacent to given strip, and add them to the
        experiment. This is a helper function used by build.
        """
        opposite_vertex = strip.vertices[face_index + 1]
        face = strip.faces[face_index]
        other_face = strip.get_unstripped_adjacent_face(face, opposite_vertex)
        if other_face:
            winding = strip.reversed_
            if face_index & 1:
                winding = not winding
            other_strip = TriangleStrip(experiment=self)
            if winding:
                other_vertex = strip.vertices[face_index]
                face_index = other_strip.build(other_vertex, other_face)
            else:
                other_vertex = strip.vertices[face_index + 2]
                face_index = other_strip.build(other_vertex, other_face)
            self.strips.append(other_strip)
            if face_index > len(other_strip.faces) / 2:
                self.build_adjacent(other_strip, face_index - 1)
            elif face_index < len(other_strip.faces) - 1:
                self.build_adjacent(other_strip, face_index + 1)
            return True
        return False

    def find_good_reset_points(self):
        """Find a list of (at most) num_samples faces to start
        stripification, potentially after some strips have already
        been created. If no more faces are left, then it returns an
        empty list.
	"""
        good_faces = set(xrange(len(self.mesh.faces)))
        good_faces -= self.get_all_stripped_faces()
        good_faces = list(sorted(good_faces))
        reset_points = []
        stepsize = len(good_faces) / self.num_samples
        if stepsize > 2:
            return [good_faces[i]
                    for i in range(0, len(good_faces), stepsize)]
        elif good_faces:
            return [good_faces[0]]
        else:
            return []

    def score(self):
        """Remove children and find best stripification in current experiment
        tree. Returns score of experiment.
        """
        # XXX note: we want to optimize for number of strips, so maybe
        # XXX try -len(self.strips) for score?
        if self.strips:
            self_score = (float(sum(len(strip.faces)
                                    for strip in self.strips))
                          / len(self.strips))
        else:
            self_score = 0.0
        # there are children: find the one with best score
        best_child = None
        best_score = None
        for child in self.children:
            score = child.score()
            if not best_child or score > best_score:
                best_child = child
                best_score = score
        if best_child:
            self.strips += best_child.strips
            self.stripped_faces |= best_child.stripped_faces
            self_score += best_score
            self.children = []
        return self_score

class TriangleStripifier(object):
    """
    Heavily adapted from NvTriStrip.
    Origional can be found at http://developer.nvidia.com/view.asp?IO=nvtristrip_library.
    """

    def __init__(self, mesh):
        self.num_samples = 3
        self.mesh = mesh
        self.start_face_index = 0

    def find_all_strips(self):
        """Find all strips.

        Empty mesh
        ----------

        >>> m = Mesh()
        >>> m.lock()
        >>> ts = TriangleStripifier(m)
        >>> ts.find_all_strips()
        []

        Full mesh
        ---------

        >>> m = Mesh()
        >>> tmp = m.add_face(2, 1, 7)
        >>> tmp = m.add_face(0, 1, 2)
        >>> tmp = m.add_face(2, 7, 4) # in strip
        >>> tmp = m.add_face(4, 7, 11) # in strip
        >>> tmp = m.add_face(5, 3, 2)
        >>> tmp = m.add_face(1, 0, 8) # in strip
        >>> tmp = m.add_face(0, 8, 9) # bad orientation!
        >>> tmp = m.add_face(8, 0, 10) # in strip
        >>> tmp = m.add_face(10, 11, 8) # in strip
        >>> # parallel strip
        >>> tmp = m.add_face(0, 2, 21) # in strip
        >>> tmp = m.add_face(21, 2, 22) # in strip
        >>> tmp = m.add_face(2, 4, 22) # in strip
        >>> tmp = m.add_face(21, 24, 0) # in strip
        >>> tmp = m.add_face(9, 0, 24) # in strip
        >>> # parallel strip, further down
        >>> tmp = m.add_face(8, 11, 31) # in strip
        >>> tmp = m.add_face(8, 31, 32) # in strip
        >>> tmp = m.add_face(31, 11, 33) # in strip
        >>> m.lock()
        >>> ts = TriangleStripifier(m)
        >>> ts.find_all_strips()
        [[11, 4, 7, 2, 1, 0, 8, 10, 11], [4, 22, 2, 21, 0, 24, 9], [2, 5, 3], [32, 8, 31, 11, 33], [0, 8, 9]]
        """
        experiment = Experiment(self.mesh)
        # as long as we can keep building the experiment
        while experiment.build():
            # score and prune the experiment tree
            experiment.score()
            # DEBUG to see progress
            #print >>sys.stderr, len(experiment.stripped_faces), len(experiment.strips)
        # final scoring
        experiment.score()
        return [strip.get_strip()
                for strip in experiment.strips]

if __name__=='__main__':
    import doctest
    doctest.testmod()
