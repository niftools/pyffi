import unittest

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
        assert self.y.a == 1
        assert self.y.b == 1

    def test_attributes(self):
        self.y.populate_attribute_values(13, None)
        assert len(self.y._names) == 2
        assert self.y._names == ['a', 'b']
        assert self.y._a_value_.get_value() == 5
        assert self.y._b_value_.get_value() == 1

    def test_get_value(self):
        self.y.a = 5
        self.y.b = 1
        assert self.y.get_attributes_values(None) == 13

    def test_int_cast(self):
        self.y.populate_attribute_values(13, None)
        assert len(self.y._items) == 2
        assert int(self.y) == 13
