"""Tests for pyffi.utils.withref module."""

import nose.tools
from pyffi.utils.withref import ref


class A:
    x = 1
    y = 2


class B:
    a = A()


def test_withref_1():
    a = A()
    with ref(a) as z:
        nose.tools.assert_equal(z.x, 1)
        nose.tools.assert_equal(z.y, 2)
        nose.tools.assert_is(a, z)


def test_withref_2():
    b = B()
    with ref(b) as z:
        nose.tools.assert_equal(z.a.x, 1)
        nose.tools.assert_equal(z.a.y, 2)
        nose.tools.assert_is(b, z)


def test_withref_3():
    b = B()
    with ref(b.a) as z:
        nose.tools.assert_equal(z.x, 1)
        nose.tools.assert_is(b.a, z)
