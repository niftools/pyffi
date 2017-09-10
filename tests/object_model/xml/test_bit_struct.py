import unittest

from nose.tools import assert_equals, assert_false, assert_true, raises

from pyffi.object_models.xml.bit_struct import BitStructBase
from pyffi.object_models.xml import BitStructAttribute as Attr


class SimpleFormat(object):
    @staticmethod
    def name_attribute(name):
        return name


class Flags(BitStructBase):
    _numbytes = 1
    _attrs = [Attr(SimpleFormat, dict(name='a', numbits='3')),
              Attr(SimpleFormat, dict(name='b', numbits='1'))]

SimpleFormat.Flags = Flags


class TestBitStruct(unittest.TestCase):

    def setUp(self):
        self.y = Flags()

    def test_value_population(self):
        self.y.populate_attribute_values(9, None)  # b1001
        assert_equals(self.y.a, 1)
        assert_equals(self.y.b, 1)

    def test_attributes(self):
        self.y.populate_attribute_values(13, None)
        assert_true(len(self.y._names), 2)
        assert_true(self.y._names, ('a', 'b'))
        assert_true(self.y._a_value_, 5)
        assert_true(self.y._b_value_, 5)

    def test_get_value(self):
        self.y.a = 5
        self.y.b = 1
        assert_equals(self.y.get_attributes_values(None), 13)

    def test_int_cast(self):
        self.y.populate_attribute_values(13, None)
        assert_true(len(self.y._items), 2)
        assert_equals(int(self.y), 13)
