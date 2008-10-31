"""Custom functions for NiTriBasedGeomData."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, NIF File Format Library and Tools.
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
#    * Neither the name of the NIF File Format Library and Tools
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

def isInterchangeable(self, other):
    """Heuristically checks if two NiTriBasedGeomData blocks describe
    the same geometry, that is, if they can be used interchangeably in
    a nif file without affecting the rendering. The check is not fool
    proof but has shown to work in most practical cases.

    @param other: Another geometry data block.
    @type other: L{NifFormat.NiTriBasedGeomData}
    @return: C{True} if the geometries are equivalent, C{False} otherwise.
    """
    # type check
    if not isinstance(other, self.cls.NiTriBasedGeomData):
        raise TypeError("argument must be of NiTriBasedGeomData type")

    # check for object identity
    if self is other:
        return True

    # check class
    if not isinstance(self, other.__class__) \
        or not isinstance(other, self.__class__):
        return False

    # check some trivial things first
    for attribute in (
        "numVertices", "keepFlags", "compressFlags", "hasVertices",
        "numUvSets", "hasNormals", "center", "radius",
        "hasVertexColors", "hasUv", "consistencyFlags"):
        if getattr(self, attribute) != getattr(other, attribute):
            return False

    # check vertices (this includes uvs, vcols and normals)
    verthashes1 = [hsh for hsh in self.getVertexHashGenerator()]
    verthashes2 = [hsh for hsh in other.getVertexHashGenerator()]
    for hash1 in verthashes1:
        if not hash1 in verthashes2:
            return False
    for hash2 in verthashes2:
        if not hash2 in verthashes1:
            return False

    # check triangle list
    triangles1 = [tuple(verthashes1[i] for i in tri)
                  for tri in self.getTriangles()]
    triangles2 = [tuple(verthashes2[i] for i in tri)
                  for tri in other.getTriangles()]
    for tri1 in triangles1:
        if not tri1 in triangles2:
            return False
    for tri2 in triangles2:
        if not tri2 in triangles1:
            return False

    # looks pretty identical!
    return True
