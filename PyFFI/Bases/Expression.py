# --------------------------------------------------------------------------
# PyFFI.Bases.Expression
# Expression parser (for arr1, arr2, and cond xml attributes of <add> tag).
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

class Expression(object):
    """This class represents an expression.
    
    >>> class A(object):
    ...     x = False
    ...     y = True
    >>> a = A()
    >>> e = Expression('x || y')
    >>> e.eval(a)
    1
    >>> Expression('99 & 15').eval(a)
    3
    >>> bool(Expression('(99&15)&&y').eval(a))
    True
    >>> a.hello_world = False
    >>> def nameFilter(s):
    ...     return 'hello_' + s.lower()
    >>> bool(Expression('(99 &15) &&WoRlD', name_filter = nameFilter).eval(a))
    False
    >>> Expression('c && d').eval(a)
    Traceback (most recent call last):
        ...
    AttributeError: 'A' object has no attribute 'c'
    >>> bool(Expression('1 == 1').eval())
    True
    >>> bool(Expression('1 != 1').eval())
    False
    """
    operators = [ '==', '!=', '>=', '&&', '||', '&', '|' ]
    def __init__(self, expr_str, name_filter = None):
        left, self._op, right = self._partition(expr_str)
        self._left = self._parse(left, name_filter)
        if right:
            self._right = self._parse(right, name_filter)
        else:
            self._right = ''

    def eval(self, data = None):
        """Evaluate the expression to an integer."""
       
        if isinstance(self._left, Expression):
            left = self._left.eval(data)
        elif isinstance(self._left, basestring):
            left = getattr(data, self._left) if self._left != '""' else ""
        else:
            assert(isinstance(self._left, (int, long))) # debug
            left = self._left

        if not self._op:
            return left

        if isinstance(self._right, Expression):
            right = self._right.eval(data)
        elif isinstance(self._right, basestring):
            right = getattr(data, self._right) if self._right != '""' else ""
        else:
            assert(isinstance(self._right, (int, long))) # debug
            right = self._right

        if self._op == '==':
            return int(left == right)
        elif self._op == '!=':
            return int(left != right)
        elif self._op == '>=':
            return int(left >= right)
        elif self._op == '&&':
            return int(left and right)
        elif self._op == '||':
            return int(left or right)
        elif self._op == '&':
            return left & right
        elif self._op == '|':
            return left | right
        else:
            raise NotImplementedError("expression syntax error: operator '" + op + "' not implemented")

    def __str__(self):
        """Reconstruct the expression to a string."""
        
        left = str(self._left)
        if not self._op: return left
        right = str(self._right)
        return left + ' ' + self._op + ' ' + right

    @classmethod
    def _parse(cls, expr_str, name_filter = None):
        """Returns an Expression, string, or int, depending on the
        contents of <expr_str>."""
        # brackets or operators => expression
        if ("(" in expr_str) or (")" in expr_str):
            return Expression(expr_str, name_filter)
        for op in cls.operators:
            if expr_str.find(op) != -1:
                return Expression(expr_str, name_filter)
        # try to convert it to an integer
        try:
            return int(expr_str)
        # failed, so return the string, passed through the name filter
        except ValueError:
            return name_filter(expr_str) if name_filter else expr_str
    
    @classmethod
    def _partition(cls, expr_str):
        """Partitions expr_str. See examples below.

        >>> Expression._partition('abc || efg')
        ('abc', '||', 'efg')
        >>> Expression._partition('abc||efg')
        ('abc', '||', 'efg')
        >>> Expression._partition('abcdefg')
        ('abcdefg', '', '')
        >>> Expression._partition(' abcdefg ')
        ('abcdefg', '', '')
        >>> Expression._partition(' (a | b) & c ')
        ('a | b', '&', 'c')
        >>> Expression._partition('(a | b)!=(b&c)')
        ('a | b', '!=', 'b&c')
        >>> Expression._partition('(a== b) &&(( b!=c)||d )')
        ('a== b', '&&', '( b!=c)||d')
        """
        # check if the left hand side starts with brackets
        # and if so, find the position of the starting bracket and the ending
        # bracket
        left_startpos, left_endpos = cls._scanBrackets(expr_str)
        if left_startpos >= 0:
            # yes, it is a bracketted expression
            # so remove brackets and whitespace,
            # and let that be the left hand side
            left_str = expr_str[left_startpos+1:left_endpos].strip()
            # the next token should be the operator
            # find the position where the operator should start
            op_startpos = left_endpos+1
            while expr_str[op_startpos] == " ":
                op_startpos += 1
            # to avoid confusion between && and &, and || and |,
            # let's first scan for operators of two characters
            # and then for operators of one character
            for op_endpos in xrange(op_startpos+1, op_startpos-1, -1):
                op_str = expr_str[op_startpos:op_endpos+1]
                if op_str in cls.operators:
                    break
            else:
                raise ValueError("expression syntax error: expected operator at '%s'"%expr_str[op_startpos:])
        else:
            # it's not... so we need to scan for the first operator
            for op_startpos, ch in enumerate(expr_str):
                if ch == ' ': continue
                if ch == '(' or ch == ')':
                    raise ValueError("expression syntax error: expected operator before '%s'"%expr_str[op_startpos:])
                # to avoid confusion between && and &, and || and |,
                # let's first scan for operators of two characters
                for op_endpos in xrange(op_startpos+1, op_startpos-1, -1):
                    op_str = expr_str[op_startpos:op_endpos+1]
                    if op_str in cls.operators:
                        break
                else:
                    continue
                break
            else:
                # no operator found, so we are done
                left_str = expr_str.strip()
                op_str = ''
                right_str = ''
                return left_str, op_str, right_str
            # operator found! now get the left hand side
            left_str = expr_str[:op_startpos].strip()

        # now we have done the left hand side, and the operator
        # all that is left is to process the right hand side
        right_startpos, right_endpos = cls._scanBrackets(expr_str, op_endpos+1)
        if right_startpos >= 0:
            # yes, it is a bracketted expression
            # so remove brackets and whitespace,
            # and let that be the right hand side
            right_str = expr_str[right_startpos+1:right_endpos].strip()
            # check for trailing junk
            if expr_str[right_endpos+1:] and not expr_str[right_endpos+1:] == ' ':
                raise ValueError("expression syntax error: unexpected trailing characters '%s'"%expr_str[right_endpos+1:])
        else:
            # no, so just take the whole expression as right hand side
            right_str = expr_str[op_endpos+1:].strip()
            # check that it is a valid expression
            if ("(" in right_str) or (")" in right_str):
                raise ValueError("expression syntax error: unexpected brackets in '%s'"%right_str)
        return left_str, op_str, right_str

    @staticmethod
    def _scanBrackets(expr_str, fromIndex = 0):
        """Looks for matching brackets.

        >>> Expression._scanBrackets('abcde')
        (-1, -1)
        >>> Expression._scanBrackets('()')
        (0, 1)
        >>> Expression._scanBrackets('(abc(def))g')
        (0, 9)
        >>> s = '  (abc(dd efy 442))xxg'
        >>> startpos, endpos = Expression._scanBrackets(s)
        >>> print s[startpos+1:endpos]
        abc(dd efy 442)
        """
        startpos = -1
        endpos = -1
        scandepth = 0
        for scanpos in xrange(fromIndex, len(expr_str)):
            scanchar = expr_str[scanpos]
            if scanchar == "(":
                if startpos == -1:
                    startpos = scanpos
                scandepth += 1
            elif scanchar == ")":
                scandepth -= 1
                if scandepth == 0:
                    endpos = scanpos
                    break
        else:
            if startpos != -1 or endpos != -1:
                raise ValueError("expression syntax error (non-matching brackets?)")
        return (startpos, endpos)
