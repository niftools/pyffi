"""Tests for pyffi.utils.withref module."""

from pyffi.utils.withref import ref


class A:
    x = 1
    y = 2


class B:
    a = A()


def test_withref_1():
    a = A()
    with ref(a) as z:
        assert z.x == 1
        assert z.y == 2
        assert a is z


def test_withref_2():
    b = B()
    with ref(b) as z:
        assert z.a.x == 1
        assert z.a.y == 2
        assert b is z


def test_withref_3():
    b = B()
    with ref(b.a) as z:
        assert z.x == 1
        assert b.a is z
