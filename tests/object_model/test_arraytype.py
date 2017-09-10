from pyffi.object_models.array_type import ValidatedList
from pyffi.object_models.array_type import UniformArray
from pyffi.object_models.simple_type import SimpleType
from tests.utils import assert_tuple_values

import nose
from nose.tools import assert_equals


class IntList(ValidatedList):
    """Mock class to test validation"""

    def validate(self, item):
        """validation the type is an int"""
        if not isinstance(item, int):
            raise TypeError("item must be int")


class MyInt(SimpleType):
    """Mock class with a simple value"""
    def __init__(self, value=0):
        self._value = value


class ListOfInts(UniformArray):
    ItemType = MyInt


class TestArrayType:
    """Regression tests for pyffi.object_models.array_type."""

    @nose.tools.raises(TypeError)
    def test_invalid_array_constructor(self):
        """Test adding an invalid type to the constructor"""
        IntList([1, 2, 3.0])

    @nose.tools.raises(TypeError)
    def test_invalid_member_set(self):
        """Test setting an invalid """
        x = IntList([1, 2, 3])
        x[0] = "a"

    def test_member_set(self):
        """Test setting a value through index access"""
        x = IntList([1, 2, 3])
        x[0] = 10
        assert_equals(x[0], 10)

    @nose.tools.raises(TypeError)
    def test_invalid_append(self):
        """Test appending an invalid value type onto the list"""
        x = IntList([1, 2, 3])
        x.append(3.14)

    def test_append(self):
        """Test appending a value onto the list"""
        x = IntList([1, 2, 3])
        x.append(314)
        assert_equals(len(x), 4)
        assert_equals(x[-1], 314)

    @nose.tools.raises(TypeError)
    def test_invalid_extends(self):
        """Test extending array with a list which contains an invalid type"""
        x = IntList([1, 2, 3])
        x.extend([1, 2, 3, 4, "woops"])

    def test_extends(self):
        """Test extending array with a list"""
        x = IntList([1, 2, 3])
        x.extend([1, 2, 3, 4, 0])
        assert_equals(len(x), 8)
        assert_equals(x[-2:], [4, 0])


class TestAnyArray:
    """Test array items"""

    @nose.tools.raises(TypeError)
    def test_invalid_anytype_constructor(self):
        """Test elements must be of AnyType"""
        class InvalidListOfInts(UniformArray):
            """Mock class to uniform and override values"""
            ItemType = int

    def test_subtype_constructor(self):
        """Test subtyping setting correct ItemType with base AnyType"""
        class SubInt(SimpleType):
            """Mock class to uniform and override values"""

        class ValidListOfInts(UniformArray):
            """Mock class to uniform and override values"""
            ItemType = SubInt

    @nose.tools.raises(TypeError)
    def test_uniform_array_invalid_type_append(self):
        """Test appending incorrect type, item must be type testlist.ItemType"""
        testlist = ListOfInts()
        testlist.append(0)

    def test_uniform_array_append(self):
        """Test appending item of correct type testlist.ItemType"""
        x = MyInt(value=123)
        testlist = ListOfInts()
        testlist.append(x)
        assert_equals(testlist[-1].value, 123)

    def test_extend(self):
        """Test extending array with items of type testlist.ItemType"""
        values = (2, 10, 2)
        testlist = ListOfInts()
        testlist.extend([MyInt(value=val) for val in values])

        r_vals = [testlist[index].value for index in range(0, 1, 2)]
        assert_tuple_values(r_vals, values)

    @nose.tools.raises(TypeError)
    def test_invalid_extend(self):
        """Test extending array with invalid items not of type testlist.ItemType"""
        testlist = ListOfInts()
        testlist.extend(0)
