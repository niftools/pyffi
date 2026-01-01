from pyffi.object_models.simple_type import SimpleType


class TestSimpleType:
    """Regression tests for L{pyffi.object_models.simple_type}"""

    def test_constructor(self):
        """Test default constructor"""
        test = SimpleType()
        assert str(test) == 'None'
        assert test.value is None
        assert test._value is None

    def test_value_property(self):
        """Test simple type property access"""
        value = 'eek!'

        test = SimpleType()
        test.value = value
        assert str(test) == value
        assert test.value == value
        assert test._value == value

    def test_interchangeability(self):
        """Test simple value interchangeability check"""
        test1 = SimpleType()
        test1.value = 2
        test2 = SimpleType()
        test2.value = 2
        assert test1 is not test2
        assert test1.is_interchangeable(test2)

        test2.value = 'hello'
        assert not test1.is_interchangeable(test2)
