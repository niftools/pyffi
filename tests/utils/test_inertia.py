"""Tests for pyffi.utils.inertia module."""
import math

import pytest

from pyffi.utils.inertia import get_mass_center_inertia_polyhedron, getMassInertiaSphere
from pyffi.utils.quickhull import qhull3d
from tests.utils import assert_tuple_values


class TestInertia:
    """Tests Mass Centre Inertia generation"""

    def test_mass_inertia_sphere_solid(self):
        """Test mass and inertia for solid sphere"""
        mass, inertia_matrix = getMassInertiaSphere(2.0, 3.0)
        assert mass == pytest.approx(100.53096491)
        assert inertia_matrix[0][0] == pytest.approx(160.849543863)

    def test_inertia_polyhedron_sphere(self):
        """Test mass and inertia for simple sphere"""
        # very rough approximation of a sphere of radius 2
        poly = [(3, 0, 0), (0, 3, 0), (-3, 0, 0), (0, -3, 0), (0, 0, 3), (0, 0, -3)]
        vertices, triangles = qhull3d(poly)
        mass, center, inertia = get_mass_center_inertia_polyhedron(vertices, triangles, density=3)
        assert mass == 108.0
        assert center, (0.0, 0.0 == 0.0)
        assert_tuple_values((inertia[0][0], inertia[1][1], inertia[2][2]), (194.4, 194.4, 194.4))
        assert_tuple_values((inertia[0][1], inertia[0][2], inertia[1][2]), (0, 0, 0))

    def test_inertia_polyhedron_sphere_accurate(self):
        """Test mass and inertia for accurate sphere"""
        sphere = []
        n = 10
        for j in range(-n + 1, n):
            theta = j * 0.5 * math.pi / n
            st, ct = math.sin(theta), math.cos(theta)
            m = max(3, int(ct * 2 * n + 0.5))
            for i in range(0, m):
                phi = i * 2 * math.pi / m
                s, c = math.sin(phi), math.cos(phi)
                sphere.append((2 * s * ct, 2 * c * ct, 2 * st))  # construct sphere of radius 2
        sphere.append((0, 0, 2))
        sphere.append((0, 0, -2))
        vertices, triangles = qhull3d(sphere)
        mass, center, inertia = get_mass_center_inertia_polyhedron(vertices, triangles, density=3, solid=True)

        assert mass - 100.53 < 10  # 3*(4/3)*pi*2^3 = 100.53
        assert sum(abs(x) for x in center) < 0.01  # is center at origin?
        assert abs(inertia[0][0] - 160.84) < 10
        mass, center, inertia = get_mass_center_inertia_polyhedron(vertices, triangles, density=3, solid=False)
        assert abs(mass - 150.79) < 10  # 3*4*pi*2^2 = 150.79
        assert abs(inertia[0][0] - mass * 0.666 * 4) < 20  # m*(2/3)*2^2

    def test_inertia_polyhedron_box(self):
        """Get mass and inertia for box"""
        box = [(0, 0, 0), (1, 0, 0), (0, 2, 0), (0, 0, 3), (1, 2, 0), (0, 2, 3), (1, 0, 3), (1, 2, 3)]
        vertices, triangles = qhull3d(box)
        mass, center, inertia = get_mass_center_inertia_polyhedron(vertices, triangles, density=4)
        assert mass == 24.0
        assert_tuple_values(center, (0.5, 1.0, 1.5))
        assert_tuple_values(inertia[0], (26.0, 0.0, 0.0))
        assert_tuple_values(inertia[1], (0.0, 20.0, 0.0))
        assert_tuple_values(inertia[2], (0.0, 0.0, 10.0))
