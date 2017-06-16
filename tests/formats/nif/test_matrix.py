from pyffi.formats.nif import NifFormat
from nose.tools import assert_equals, assert_true, assert_false, assert_almost_equals
from tests.utils import assert_tuple_values


class TestMatrix:
    """Test NifFormat.Matrix related classes"""

    def test_scale_rot_translate(self):
        """Matrix tests for scale, rotation, and translation"""

        mat = NifFormat.Matrix44()
        mat.set_identity()

        identity = ((1.000, 0.000, 0.000, 0.000),
                    (0.000, 1.000, 0.000, 0.000),
                    (0.000, 0.000, 1.000, 0.000),
                    (0.000, 0.000, 0.000, 1.000))
        assert_tuple_values(mat.as_tuple(), identity)

        s, r, t = mat.get_scale_rotation_translation()
        assert_equals(s, 1.0)

        rotation = ((1.000, 0.000, 0.000),
                    (0.000, 1.000, 0.000),
                    (0.000, 0.000, 1.000))

        assert_tuple_values(r.as_tuple(), rotation)

        translation = (0.000, 0.000, 0.000)
        assert_tuple_values(t.as_tuple(), translation)
        assert_true(mat.get_matrix_33().is_scale_rotation())

        mat.m_21 = 2.0
        assert_false(mat.get_matrix_33().is_scale_rotation())

    def test_det_inverse_matrices(self):
        """Tests matrix determinants and inverse matrices"""
        mat = NifFormat.Matrix33()
        mat.m_11 = -0.434308
        mat.m_12 = 0.893095
        mat.m_13 = -0.117294
        mat.m_21 = -0.451770
        mat.m_22 = -0.103314
        mat.m_23 = 0.886132
        mat.m_31 = 0.779282
        mat.m_32 = 0.437844
        mat.m_33 = 0.448343
        assert_true(mat == mat)
        assert_false(mat != mat)

        assert_almost_equals(mat.get_determinant(), 0.9999995)
        assert_true(mat.is_rotation())

        transpose = ((-0.434308, -0.45177, 0.779282),
                     (0.893095, -0.103314, 0.437844),
                     (-0.117294, 0.886132, 0.448343))

        t = mat.get_transpose()
        tup = t.as_tuple()
        assert_tuple_values(tup, transpose)
        assert_true(mat.get_inverse() == mat.get_transpose())

        mat *= 0.321
        assert_true(mat.get_scale(), 0.32100)

        s, r = mat.get_inverse().get_scale_rotation()
        assert_almost_equals(s, 3.11526432)
        assert_true(abs(0.321 - 1/s) < NifFormat.EPSILON)

        rotation = ((-0.43430806610505857, -0.45177006876291087, 0.7792821186127868),
                    (0.8930951359360114, -0.10331401572519507, 0.43784406664326525),
                    (-0.11729401785305989, 0.8861321348761886, 0.4483430682412948))

        assert_tuple_values(r.as_tuple(), rotation)

        assert_true(abs(mat.get_determinant() - 0.321 ** 3) < NifFormat.EPSILON)

        mat *= -2

        applied_scale = ((0.27882573600000005, -0.57336699, 0.075302748),
                         (0.29003634, 0.066327588, -0.568896744),
                         (-0.500299044, -0.28109584800000004, -0.287836206))
        assert_tuple_values(mat.as_tuple(), applied_scale)

        assert_almost_equals(mat.get_scale(), -0.6419999)
        assert_true(abs(mat.get_determinant() + 0.642 ** 3) < NifFormat.EPSILON)

        mat2 = NifFormat.Matrix44()
        mat2.set_identity()
        mat2.set_matrix_33(mat)
        t = NifFormat.Vector3()
        t.x = 1.2
        t.y = 3.4
        t.z = 5.6
        mat2.set_translation(t)

        mat_tuple = ((0.27882573600000005, -0.57336699, 0.075302748, 0.0),
                     (0.29003634, 0.066327588, -0.568896744, 0.0),
                     (-0.500299044, -0.28109584800000004, -0.287836206, 0.0),
                     (1.2, 3.4, 5.6, 1.0))

        assert_tuple_values(mat2.as_tuple(), mat_tuple)

        assert_true(mat2 == mat2)
        assert_false(mat2 != mat2)

        inverse = ((0.6764922116181463, 0.703691588556347, -1.2138348905712357, 0.0),
                   (-1.391113706712997, 0.1609252335925591, -0.68199999977835, 0.0),
                   (0.18270093452006145, -1.3802679123239985, -0.6983535823275522, 0.0),
                   (2.89487071557007, 6.337924608532074, 7.686181928966164, 1.0))

        assert_tuple_values(mat2.get_inverse().as_tuple(), inverse)

        precise_inverse = ((0.6764920349300052, 0.7036909221331374, -1.213835361467897, 0.0),
                           (-1.3911137728067433, 0.16092507151327615, -0.6820005092926544, -0.0),
                           (0.18270108550032338, -1.380268558209707, -0.698354874744861, 0.0),
                           (2.8948703068251107, 6.337929576269453, 7.686191463927723, 1.0))

        assert_tuple_values(mat2.get_inverse(fast=False).as_tuple(), precise_inverse)
        assert_true((mat2 * mat2.get_inverse()).is_identity())

    def test_sup_norm(self):
        """Test sup norm of a matrix"""
        mat = NifFormat.Matrix44()
        mat.set_identity()
        assert_equals(mat.sup_norm(), 1.0)
        mat.m_11 = -0.434308
        mat.m_12 = 0.893095
        mat.m_13 = -0.117294
        mat.m_21 = -0.451770
        mat.m_22 = -0.103314
        mat.m_23 = 0.886132
        mat.m_31 = 0.779282
        mat.m_32 = 0.437844
        mat.m_33 = 0.448343
        mat.m_41 = 3
        mat.m_41 = 4
        mat.m_41 = 8
        assert_equals(mat.sup_norm(), 8.0)
