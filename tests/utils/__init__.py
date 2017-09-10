"""Tests for utility classes"""

import nose
import nose.tools


def assert_tuple_values(a, b):
    """Wrapper func to cleanly assert tuple values"""
    for i, j in zip(a, b):
        nose.tools.assert_almost_equal(i, j)
