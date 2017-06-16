from pyffi.formats.nif import NifFormat
import nose

def test_bhkPackedNiTriStripsShape():

    # Adding Shapes
    shape = NifFormat.bhkPackedNiTriStripsShape()
    nose.tools.assert_equal(shape.num_sub_shapes, 0)
    nose.tools.assert_true(shape.data is None)
    triangles1 = [(0, 1, 2)]
    normals1 = [(1, 0, 0)]
    vertices1 = [(0, 0, 0), (0, 0, 1), (0, 1, 0)]
    triangles2 = [(0, 2, 1), (1, 2, 3)]
    normals2 = [(1, 0, 0), (-1, 0, 0)]
    vertices2 = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 0, 0)]
    shape.add_shape(triangles=triangles1, normals=normals1, vertices=vertices1, layer=1, material=2)
    shape.add_shape(triangles=triangles2, normals=normals2, vertices=vertices2, layer=3, material=4)
    nose.tools.assert_equal(shape.num_sub_shapes, 2)
    nose.tools.assert_equal(shape.sub_shapes[0].layer, 1)
    nose.tools.assert_equal(shape.sub_shapes[0].num_vertices, 3)
    nose.tools.assert_equal(shape.sub_shapes[0].material.material, 2)
    nose.tools.assert_equal(shape.sub_shapes[1].layer, 3)
    nose.tools.assert_equal(shape.sub_shapes[1].num_vertices, 4)
    nose.tools.assert_equal(shape.sub_shapes[1].material.material, 4)

    # for fallout 3 the subshape info is stored in the shape data
    nose.tools.assert_equal(shape.data.num_sub_shapes, 2)
    nose.tools.assert_equal(shape.data.sub_shapes[0].layer, 1)
    nose.tools.assert_equal(shape.data.sub_shapes[0].num_vertices, 3)
    nose.tools.assert_equal(shape.data.sub_shapes[0].material.material, 2)
    nose.tools.assert_equal(shape.data.sub_shapes[1].layer, 3)
    nose.tools.assert_equal(shape.data.sub_shapes[1].num_vertices, 4)
    nose.tools.assert_equal(shape.data.sub_shapes[1].material.material, 4)
    nose.tools.assert_equal(shape.data.num_triangles, 3)
    nose.tools.assert_equal(shape.data.num_vertices, 7)

