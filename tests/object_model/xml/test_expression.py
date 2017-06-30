import unittest

from pyffi.object_models.xml.expression import Expression
from nose.tools import assert_equals, assert_false, assert_true, raises


class A(object):
    x = False
    y = True


class B(object):

    def __int__(self):
        return 7

    def __mul__(self, other):
        return self.__int__() * int(other)


class TestExpression(unittest.TestCase):

    def setUp(self):
        self.a = A()

    def test_data_source_evaluation(self):
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

class TestPartition:

    def test_partition_empty(self):
        assert_equals(Expression._partition(''), ('', '', ''))

    def test_partition_left(self):
        assert_equals(Expression._partition('abcdefg'), ('abcdefg', '', ''))

    def test_partition_left_trim(self):
        assert_equals(Expression._partition(' abcdefg '), ('abcdefg', '', ''))

    def test_partition_logical_or(self):
        assert_equals(Expression._partition('abc || efg'), ('abc', '||', 'efg'))

    def test_partition_equivilance(self):
        assert_equals(Expression._partition('(1 == 1)'), ('1 == 1', '', ''))

    def test_multi_brances(self):
        assert_equals(Expression._partition('( 1 != 1 ) || ((!abc) == 1)'), ('1 != 1', '||', '(!abc) == 1'))

    def test_partition_no_spaces(self):
        assert_equals(Expression._partition('abc||efg'), ('abc', '||', 'efg'))

    def test_partition_bit_ops(self):
        assert_equals(Expression._partition(' (a | b) & c '), ('a | b', '&', 'c'))

    def test_partition_right_uninary_op(self):
        assert_equals(Expression._partition('!(1 <= 2)'), ('', '!', '(1 <= 2)'))

    def test_partition_not_eq(self):
        assert_equals(Expression._partition('(a | b)!=(b&c)'), ('a | b', '!=', 'b&c'))

    def test_partition_left_trim(self):
        assert_equals(Expression._partition('(a== b) &&(( b!=c)||d )'), ('a== b', '&&', '( b!=c)||d'))


class TestBraces:

    def test_no_brace(self):
        assert_equals(Expression._scan_brackets('abcde'), (-1, -1))

    def test_single_set_of_braces(self):
        assert_equals(Expression._scan_brackets('()'), (0, 1))

    def test_nested_braces(self):
        assert_equals(Expression._scan_brackets('(abc(def))g'), (0, 9))

        s = '  (abc(dd efy 442))xxg'
        start_pos, end_pos = Expression._scan_brackets(s)
        assert_equals(s[start_pos + 1:end_pos], "abc(dd efy 442)")