"""Algorithms to reorder triangle list order and vertex order aiming to
minimize vertex cache misses.

This is effectively an implementation of
'Linear-Speed Vertex Cache Optimisation' by Tom Forsyth, 28th September 2006
http://home.comcast.net/~tom_forsyth/papers/fast_vert_cache_opt.html
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

import collections

class VertexInfo:
    """Stores information about a vertex."""

    # constants used for scoring algorithm
    CACHE_SIZE = 32 # higher values yield virtually no improvement
    """The size of the modeled cache."""

    CACHE_DECAY_POWER = 1.5
    LAST_TRI_SCORE = 0.75
    VALENCE_BOOST_SCALE = 2.0
    VALENCE_BOOST_POWER = 0.5

    def __init__(self, cache_position=-1, score=-1,
                 face_indices=None):
        self.cache_position = cache_position
        self.score = score
        self.face_indices = ([] if face_indices is None
                             else face_indices)

    def update_score(self):
        if not self.face_indices:
            # no triangle needs this vertex
            self.score = -1
            return

        if self.cache_position < 0:
            # not in cache
            self.score = 0
        elif self.cache_position >= 0 and self.cache_position < 3:
            # used in last triangle
            self.score = self.LAST_TRI_SCORE
        else:
            self.score = (
                (1.0 - (self.cache_position - 3) / (self.CACHE_SIZE - 3))
                ** self.CACHE_DECAY_POWER)

        # bonus points for having low number of triangles still in use
        self.score += self.VALENCE_BOOST_SCALE * (
            len(self.face_indices) ** (-self.VALENCE_BOOST_POWER))

class FaceInfo:
    def __init__(self, added=False, score=0.0, vertex_indices=None):
        self.added = False
        self.score = 0.0
        self.vertex_indices = ([] if vertex_indices is None
                               else vertex_indices)

class Mesh:
    """Simple mesh implementation which keeps track of which triangles
    are used by which vertex, and vertex cache positions.
    """

    def __init__(self, faces):
        """Initialize mesh from given set of faces.

        Empty mesh
        ----------

        >>> Mesh([]).face_infos
        []

        Single triangle mesh (with degenerate)
        --------------------------------------

        >>> m = Mesh([(0,1,2), (1,2,0)])
        >>> [vertex_info.face_indices for vertex_info in m.vertex_infos]
        [[0], [0], [0]]
        >>> [face_info.vertex_indices for face_info in m.face_infos]
        [(0, 1, 2)]

        Double triangle mesh
        --------------------

        >>> m = Mesh([(0,1,2), (2,1,3)])
        >>> [vertex_info.face_indices for vertex_info in m.vertex_infos]
        [[0], [0, 1], [0, 1], [1]]
        >>> [face_info.vertex_indices for face_info in m.face_infos]
        [(0, 1, 2), (1, 3, 2)]
        """
        # initialize vertex and face information, and vertex cache
        self.vertex_infos = []
        self.face_infos = []
        # add all vertices
        if faces:
            num_vertices = max(max(verts) for verts in faces) + 1
        else:
            num_vertices = 0
        self.vertex_infos = [VertexInfo() for i in xrange(num_vertices)]
        # add all faces
        _added_faces = set([])
        face_index = 0
        for v0, v1, v2 in faces:
            if v0 == v1 or v1 == v2 or v2 == v0:
                # skip degenerate faces
                continue
            if v0 < v1 and v0 < v2:
                verts = (v0, v1, v2)
            elif v1 < v0 and v1 < v2:
                verts = (v1, v2, v0)
            elif v2 < v0 and v2 < v1:
                verts = (v2, v0, v1)
            if verts not in _added_faces:
                self.face_infos.append(FaceInfo(vertex_indices=verts))
                for vertex in verts:
                    self.vertex_infos[vertex].face_indices.append(
                        face_index)
                face_index += 1
                _added_faces.add(verts)
        # calculate score of all vertices
        for vertex_info in self.vertex_infos:
            vertex_info.update_score()
        # calculate score of all triangles
        for face_info in self.face_infos:
            face_info.score = sum(
                self.vertex_infos[vertex].score
                for vertex in face_info.vertex_indices)

    def get_cache_optimized_faces(self):
        """Reorder faces in a cache efficient way.

        >>> m = Mesh([(0,1,2), (7,8,9),(2,3,4)])
        >>> m.get_cache_optimized_faces()
        [(7, 8, 9), (0, 1, 2), (2, 3, 4)]
        """
        faces = []
        cache = collections.deque()
        while any(not face_info.added for face_info in self.face_infos):
            # pick face with highest score
            best_face_index, best_face_info = max(
                (face
                 for face in enumerate(self.face_infos)
                 if not face[1].added),
                key=lambda face: face[1].score)
            # mark as added
            best_face_info.added = True
            # append to ordered list of faces
            faces.append(best_face_info.vertex_indices)
            # keep list of vertices and faces whose score we will need
            # to update
            updated_vertices = set([])
            updated_faces = set([])
            # for each vertex in the just added face
            for vertex in best_face_info.vertex_indices:
                vertex_info = self.vertex_infos[vertex]
                # update face indices
                vertex_info.face_indices.remove(best_face_index)
                # must update its score
                updated_vertices.add(vertex)
                updated_faces.update(vertex_info.face_indices)
                # add vertices to cache (score is updated later)
                if vertex not in cache:
                    cache.appendleft(vertex)
                    if len(cache) > VertexInfo.CACHE_SIZE:
                        # cache overflow!
                        # remove vertex from cache
                        removed_vertex = cache.pop()
                        removed_vertex_info = self.vertex_infos[removed_vertex]
                        # update its cache position
                        removed_vertex_info.cache_position = -1
                        # must update its score
                        updated_vertices.add(removed_vertex)
                        updated_faces.update(removed_vertex_info.face_indices)
            # for each vertex in the cache (this includes those from the
            # just added face)
            for i, vertex in enumerate(cache):
                vertex_info = self.vertex_infos[vertex]
                # update cache positions
                vertex_info.cache_position = i
                # must update its score
                updated_vertices.add(vertex)
                updated_faces.update(vertex_info.face_indices)
            # update scores
            for vertex in updated_vertices:
                self.vertex_infos[vertex].update_score()
            for face in updated_faces:
                face_info = self.face_infos[face]
                face_info.score = sum(
                    self.vertex_infos[vertex].score
                    for vertex in face_info.vertex_indices)
        # return result
        return faces

if __name__=='__main__':
    import doctest
    doctest.testmod()
