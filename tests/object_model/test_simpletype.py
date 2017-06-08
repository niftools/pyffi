import nose
from nose.tools import assert_equals, assert_is_none, assert_false, assert_true

from pyffi.object_models.simple_type import SimpleType


class TestSimpleType:
    """Regression tests for L{pyffi.object_models.simple_type}"""

    def test_constructor(self):
        """Test default constructor"""
        test = SimpleType()
        assert_equals(str(test), 'None')
        assert_is_none(test.value)
        assert_is_none(test._value)

    def test_value_property(self):
        """Test simple type property access"""
        value = 'eek!'

        test = SimpleType()
        test.value = value
        assert_equals(str(test), value)
        assert_equals(test.value, value)
        assert_equals(test._value, value)

    def test_interchangeability(self):
        """Test simple value interchangeability check"""
        test1 = SimpleType()
        test1.value = 2
        test2 = SimpleType()
        test2.value = 2
        assert_false(test1 is test2)
        assert_true(test1.is_interchangeable(test2))

        test2.value = 'hello'
        assert_false(test1.is_interchangeable(test2))
