from pyffi.object_models.xml.expression import Expression

from tests.utils import assert_tuple_values

from nose.tools import assert_equals, assert_false, assert_true, raises


class A(object):
    x = False
    y = True

class B(object):

    def __int__(self):
        return 7

    def __mul__(self, other):
        return self.__int__() * int(other)


class TestExpression:

    def setUp(self):
        self.a = A()

    def test_data_source_evaluation(self):
        self.a = A()
        e = Expression('x || y')
        assert_equals(e.eval(self.a), 1)

        assert_equals(Expression('99 & 15').eval(self.a), 3)
        assert_true(bool(Expression('(99&15)&&y').eval(self.a)))

    def test_name_filter(self):
        self.a.hello_world = False

        def nameFilter(s):
            return 'hello_' + s.lower()

        assert_false(bool(Expression('(99 &15) &&WoRlD', name_filter = nameFilter).eval(self.a)))

    @raises(AttributeError)
    def test_attribute_error(self):
        Expression('c && d').eval(self.a)

    def test_expression_operators(self):
        assert_true(bool(Expression('1 == 1').eval()))
        assert_true(bool(Expression('(1 == 1)').eval()))
        assert_false(bool(Expression('1 != 1').eval()))
        assert_false(bool(Expression('!(1 == 1)').eval()))
        assert_false(bool(Expression('!((1 <= 2) && (2 <= 3))').eval()))
        assert_true(bool(Expression('(1 <= 2) && (2 <= 3) && (3 <= 4)').eval()))

    def test_implicit_cast(self):
        self.a.x = B()
        assert_equals(Expression('x * 10').eval(self.a), 70)

