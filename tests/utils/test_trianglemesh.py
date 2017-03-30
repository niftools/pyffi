"""Tests for pyffi.utils.withref module."""

import nose.tools
from pyffi.utils.trianglemesh import Face

indices = (3, 5, 7)
dupes = (10, 0, 10)
face = Face(*indices)

def test_face_list():
    nose.tools.assert_equals(indices, face.verts)


@nose.tools.raises(ValueError)
def test_duplicates():
    Face(*dupes)


def test_get_next_vertex():
    nose.tools.assert_equals(face.get_next_vertex(indices[0]), indices[1])
    nose.tools.assert_equals(face.get_next_vertex(indices[1]), indices[2])
    nose.tools.assert_equals(face.get_next_vertex(indices[2]), indices[0])

@nose.tools.raises(ValueError)
def test_get_next_vertex_out_of_bounds():
    face.get_next_vertex(10)