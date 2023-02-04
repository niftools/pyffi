from pyffi.formats.nif import NifFormat


def test_bhkPackedNiTriStripsShape():
    # Adding Shapes
    shape = NifFormat.bhkPackedNiTriStripsShape()
    assert shape.num_sub_shapes == 0
    assert shape.data is None
    triangles1 = [(0, 1, 2)]
    normals1 = [(1, 0, 0)]
    vertices1 = [(0, 0, 0), (0, 0, 1), (0, 1, 0)]
    triangles2 = [(0, 2, 1), (1, 2, 3)]
    normals2 = [(1, 0, 0), (-1, 0, 0)]
    vertices2 = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 0, 0)]
    shape.add_shape(triangles=triangles1, normals=normals1, vertices=vertices1, layer=1, material=2)
    shape.add_shape(triangles=triangles2, normals=normals2, vertices=vertices2, layer=3, material=4)
    assert shape.num_sub_shapes == 2
    assert shape.sub_shapes[0].layer == 1
    assert shape.sub_shapes[0].num_vertices == 3
    assert shape.sub_shapes[0].material.material == 2
    assert shape.sub_shapes[1].layer == 3
    assert shape.sub_shapes[1].num_vertices == 4
    assert shape.sub_shapes[1].material.material == 4

    # for fallout 3 the subshape info is stored in the shape data
    assert shape.data.num_sub_shapes == 2
    assert shape.data.sub_shapes[0].layer == 1
    assert shape.data.sub_shapes[0].num_vertices == 3
    assert shape.data.sub_shapes[0].material.material == 2
    assert shape.data.sub_shapes[1].layer == 3
    assert shape.data.sub_shapes[1].num_vertices == 4
    assert shape.data.sub_shapes[1].material.material == 4
    assert shape.data.num_triangles == 3
    assert shape.data.num_vertices == 7
