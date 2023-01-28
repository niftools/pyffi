import unittest
import pytest

from pyffi.object_models.expression import Expression


class Z(object):
    a = 1
    b = 2
    c = 3


class A(object):
    x = False
    y = True
    z = Z()


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
        assert e.eval(self.a) == 1

        assert Expression('99 & 15').eval(self.a) == 3
        assert bool(Expression('(99&15)&&y').eval(self.a))

    def test_name_filter(self):
        self.a.hello_world = False

        def name_filter(s):
            return 'hello_' + s.lower()

        assert not bool(Expression('(99 &15) &&WoRlD', name_filter=name_filter).eval(self.a))

    def test_attribute_error(self):
        with pytest.raises(AttributeError):
            Expression('c && d').eval(self.a)

    def test_expression_operators(self):
        assert bool(Expression('1 == 1').eval())
        assert bool(Expression('(1 == 1)').eval())
        assert not bool(Expression('1 != 1').eval())
        assert not bool(Expression('!(1 == 1)').eval())
        assert not bool(Expression('!((1 <= 2) && (2 <= 3))').eval())
        assert bool(Expression('(1 <= 2) && (2 <= 3) && (3 <= 4)').eval())

    def test_implicit_cast(self):
        self.a.x = B()
        assert Expression('x * 10').eval(self.a) == 70
    
    def test_nested_attributes(self):
        assert bool(Expression("z.a == 1").eval(self.a))
        assert bool(Expression("z.b == 2").eval(self.a))
        assert bool(Expression("z.c == 3").eval(self.a))


class TestPartition:
    def test_partition_empty(self):
        assert Expression._partition('') == ('', '', '')

    def test_partition_left(self):
        assert Expression._partition('abcdefg') == ('abcdefg', '', '')

    def test_partition_left_trim(self):
        assert Expression._partition(' abcdefg ') == ('abcdefg', '', '')

    def test_partition_logical_or(self):
        assert Expression._partition('abc || efg') == ('abc', '||', 'efg')

    def test_partition_equivilance(self):
        assert Expression._partition('(1 == 1)') == ('1 == 1', '', '')

    def test_multi_brances(self):
        assert Expression._partition('( 1 != 1 ) || ((!abc) == 1)') == ('1 != 1', '||', '(!abc) == 1')

    def test_partition_no_spaces(self):
        assert Expression._partition('abc||efg') == ('abc', '||', 'efg')

    def test_partition_bit_ops(self):
        assert Expression._partition(' (a | b) & c ') == ('a | b', '&', 'c')

    def test_partition_right_uninary_op(self):
        assert Expression._partition('!(1 <= 2)') == ('', '!', '(1 <= 2)')

    def test_partition_not_eq(self):
        assert  Expression._partition('(a | b)!=(b&c)') == ('a | b', '!=', 'b&c')

    def test_partition_left_trim2eletricboogaloo(self):  # TODO: Had a duplicate name, give an appropriate one
        assert  Expression._partition('(a== b) &&(( b!=c)||d )') == ('a== b', '&&', '( b!=c)||d')


class TestBraces:
    def test_no_brace(self):
        assert Expression._scan_brackets('abcde') == (-1, -1)

    def test_single_set_of_braces(self):
        assert Expression._scan_brackets('()') == (0, 1)

    def test_nested_braces(self):
        assert Expression._scan_brackets('(abc(def))g') == (0, 9)

        expr_string = '  (abc(dd efy 442))xxg'
        start_pos, end_pos = Expression._scan_brackets(expr_string)
        assert expr_string[start_pos + 1:end_pos] == "abc(dd efy 442)"
