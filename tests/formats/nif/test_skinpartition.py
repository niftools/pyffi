from pyffi.formats.nif import NifFormat
from nose.tools import assert_equals


class TestSkinPartition:
    """Regression tests for NifFormat.SkinPartition"""

    def test_skinpartition_get_triangles(self):
        """Test NifFormat.SkinPartition get_triangles"""

        part = NifFormat.SkinPartition()
        part.num_vertices = 8
        part.vertex_map.update_size()
        part.vertex_map[0] = 2
        part.vertex_map[1] = 3
        part.vertex_map[2] = 4
        part.vertex_map[3] = 5
        part.vertex_map[4] = 6
        part.vertex_map[5] = 7
        part.vertex_map[6] = 1
        part.vertex_map[7] = 0
        part.num_strips = 2
        part.strip_lengths.update_size()
        part.strip_lengths[0] = 5
        part.strip_lengths[1] = 4
        part.strips.update_size()
        part.strips[0][0] = 0
        part.strips[0][1] = 2
        part.strips[0][2] = 4
        part.strips[0][3] = 3
        part.strips[0][4] = 1
        part.strips[1][0] = 5
        part.strips[1][1] = 7
        part.strips[1][2] = 5
        part.strips[1][3] = 6

        expected_tris = [(0, 2, 4), (2, 3, 4), (4, 3, 1), (7, 6, 5)]
        assert_equals(list(part.get_triangles()), expected_tris)

        expected_mapped_tris = [(2, 4, 6), (4, 5, 6), (6, 5, 3), (0, 1, 7)]
        assert_equals(list(part.get_mapped_triangles()), expected_mapped_tris)


    def test_skinpartition_update_triangles(self):
        """Test NifFormat.SkinPartition updating triangle"""
        part = NifFormat.SkinPartition()
        part.num_vertices = 8
        part.vertex_map.update_size()
        part.vertex_map[0] = 2
        part.vertex_map[1] = 3
        part.vertex_map[2] = 4
        part.vertex_map[3] = 5
        part.vertex_map[4] = 6
        part.vertex_map[5] = 7
        part.vertex_map[6] = 1
        part.vertex_map[7] = 0
        part.num_triangles = 6
        part.triangles.update_size()
        part.triangles[0].v_1 = 3
        part.triangles[0].v_2 = 2
        part.triangles[0].v_3 = 1
        part.triangles[1].v_1 = 0
        part.triangles[1].v_2 = 2
        part.triangles[1].v_3 = 4
        part.triangles[2].v_1 = 1
        part.triangles[2].v_2 = 3
        part.triangles[2].v_3 = 5
        part.triangles[3].v_1 = 0
        part.triangles[3].v_2 = 1
        part.triangles[3].v_3 = 2
        part.triangles[4].v_1 = 3
        part.triangles[4].v_2 = 4
        part.triangles[4].v_3 = 5
        part.triangles[5].v_1 = 6
        part.triangles[5].v_2 = 7
        part.triangles[5].v_3 = 6
        expected_indices = [(5, 4, 3), (2, 4, 6), (3, 5, 7), (2, 3, 4), (5, 6, 7), (1, 0, 1)]
        assert_equals(list(part.get_mapped_triangles()), expected_indices)
