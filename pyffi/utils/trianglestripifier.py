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

from pyffi.utils.trianglemesh import Face, Mesh

class TriangleStrip(object):
    """
    Heavily adapted from NvTriStrip.
    Origional can be found at http://developer.nvidia.com/view.asp?IO=nvtristrip_library.
    """

    def __init__(self, stripped_faces=None,
                 faces=None, vertices=None, reversed_=False):
        """Initialise the triangle strip."""
        self.faces = faces if faces else []
        self.vertices = vertices if vertices else []
        self.reversed_ = reversed_

        # set of indices of stripped faces
        self.stripped_faces = stripped_faces if stripped_faces else set()

    def __repr__(self):
        return ("TriangleStrip(stripped_faces=%s, faces=%s, vertices=%s, reversed_=%s)"
                % (repr(self.stripped_faces), repr(self.faces),
                   repr(self.vertices), repr(self.reversed_)))

    def get_unstripped_adjacent_face(self, face, vi):
        """Get adjacent face which is not yet stripped."""
        for otherface in face.get_adjacent_faces(vi):
            if otherface.index not in self.stripped_faces:
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
            self.stripped_faces.add(next_face.index)
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
            next_face = self.get_unstripped_adjacent_face(start_face, pv0)
        return count

    def build(self, start_vertex, start_face):
        """Builds the face strip forwards, then backwards. Returns
        index of start_face.

        >>> m = Mesh()
        >>> face = m.add_face(0, 1, 2)
        >>> m.lock()
        >>> t = TriangleStrip()
        >>> t.build(0, face)
        0
        >>> t
        TriangleStrip(stripped_faces=set([0]), faces=[Face(0, 1, 2)], vertices=[0, 1, 2], reversed_=False)
        >>> t.build(1, face)
        0
        >>> t
        TriangleStrip(stripped_faces=set([0]), faces=[Face(0, 1, 2)], vertices=[1, 2, 0], reversed_=False)
        >>> t.build(2, face)
        0
        >>> t
        TriangleStrip(stripped_faces=set([0]), faces=[Face(0, 1, 2)], vertices=[2, 0, 1], reversed_=False)
        """
        del self.faces[:]
        del self.vertices[:]
        self.reversed_ = False
        v0 = start_vertex
        v1 = start_face.get_next_vertex(v0)
        v2 = start_face.get_next_vertex(v1)
        self.stripped_faces.add(start_face.index)
        self.faces.append(start_face)
        self.vertices.append(v0)
        self.vertices.append(v1)
        self.vertices.append(v2)
        self.traverse_faces(v0, start_face, True)
        return self.traverse_faces(v2, start_face, False)

    def get_strip(self):
        """Get strip in forward winding."""
        strip = []
        if self._reversed:
            if len(self.vertices) & 1:
                strip = list(reversed(self.vertices))
            elif len(self.vertices == 4):
                strip = list(self.vertices[i] for i in (0, 2, 1, 3))
            else:
                strip = list(self.vertices)
                strip.insert(0, strip[0])
        else:
            strip = list(self.vertices)
        return strip

class Experiment(object):
    def __init__(self, start_vertex, start_face):
        self.stripped_faces = None
        self.start_vertex = start_vertex
        self.start_face = start_face
        self.strips = []

    def deepcopy(self):
        # deepcopy could be useful at some point to spawn new
        # experiments from this experiment
        result = Experiment(self.start_face, self.start_vertex)
        result.stripped_faces = self.stripped_faces.copy()
        result.strips = self.strips[:] # copies list, not just a reference to it

    def build(self, stripped_faces):
        """Build strips, starting from start_vertex and start_face."""
        # keep link to set of stripped faces
        self.stripped_faces = stripped_faces
        # build initial strip
        strip = TriangleStrip(stripped_faces=self.stripped_faces)
        strip.build(self.start_vertex, self.start_face)
        strips.append(strip)
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
            other_strip = TriangleStrip(stripped_faces=self.stripped_faces)
            if winding:
                other_vertex = strip.vertices[face_index]
                face_index = other_strip.build(other_vertex, other_face)
            else:
                other_vertex = strip.vertices[face_index + 2]
                face_index = other_strip.build(other_vertex, other_face)
            strips.append(other_strip)
            if face_index > len(other_strip.faces) / 2:
                self.build_adjacent(other_strip, face_index - 1)
            elif face_index < len(other_strip.faces) - 1:
                self.build_adjacent(other_strip, face_index + 1)
            return True
        return False

class ExperimentSelector(object):

    def __init__(self):
        self.best_score = -1.0
        self.best_experiment = None

    def update(self, experiment):
        """Updates best experiment with given experiment, if given
        experiment beats current experiment.
        """
        score = (sum(len(strip.faces) for strip in experiment.strips)
                 / 1.0 * len(experiment.strips))
        if score > self.best_score:
            self.best_score = score
            self.best_experiment = experiment

    def clear(self):
        """Remove best experiment, to start a fresh sequence of
        experiments.
        """
        self.best_score = -1.0
        self.best_experiment = None

class TriangleStripifier(object):
    """
    Heavily adapted from NvTriStrip.
    Origional can be found at http://developer.nvidia.com/view.asp?IO=nvtristrip_library.
    """

    def __init__(self, mesh):
        self.num_samples = 10
        self.mesh = mesh
        self.start_face_index = 0
        self.faces = list(self.mesh.faces.itervalues())

    def find_good_reset_point(self, stripped_faces):
        """Find a good face to start stripification, potentially
        after some strips have already been created. Result is
        stored in start_face_index. Returns True, unless no more
        faces are left.
	"""
        if not self.faces:
            return False
        self.start_face_index += len(self.faces) / self.num_samples
        if self.start_face_index >= len(self.faces):
            self.start_face_index -= len(self.faces)
        for face_index in itertools.chain(
            xrange(self.start_face_index, len(self.faces)),
            xrange(0, self.start_face_index)):
            face = self.faces[face_index]
            if face.index not in stripped_faces:
                self.start_face_index = face_index
                return True
        else:
            # we have exhausted all the faces
            return False

    def find_all_strips(self):
        """Find all strips."""
        all_strips = []
        stripped_faces = set()
        selector = ExperimentSelector()
        while True:
            experiments = []
            visited_reset_points = set()
            for sample in xrange(self.num_samples):
                if not self.find_good_reset_point(stripped_faces):
                    break
                exp_face = self.mesh.faces[self.start_face_index]
                if start_face_index in visited_reset_points:
                    continue
                visited_reset_points.add(start_face_index)
                for exp_vertex in exp_face.verts:
                    experiments.append(
                        Experiment(start_vertex=exp_vertex,
                                   start_face=exp_face))
            if not experiments:
                # done!
                return all_strips
            # note: use while loop so we only need to keep at most two
            # experiments at the same time in memory
            while experiments:
                experiment = experiments.pop()
                experiment.build(stripped_faces=stripped_faces.copy())
                selector.update(experiment)
            stripped_faces = selector.best_experiment.stripped_faces
            all_strips.extend(selector.best_experiment.strips)
            selector.clear()

if __name__=='__main__':
    import doctest
    doctest.testmod()
