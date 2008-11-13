import unittest

from antlr3 import *
from antlr3.tree import CommonTree

from FFILexer import FFILexer
from FFIParser import FFIParser

class TestFFI(unittest.TestCase):
    def createParser(self, filename):
        stream = ANTLRFileStream(filename)
        lexer = FFILexer(stream)
        tokens = CommonTokenStream(lexer)
        return FFIParser(tokens)

    def testType(self):
        parser = self.createParser("test_type.ffi")
        parser.ffi()

    def testTypeDoc(self):
        parser = self.createParser("test_type_doc.ffi")
        parser.ffi()

    def testClass(self):
        parser = self.createParser("test_class.ffi")
        parser.ffi()

    def testParameter(self):
        parser = self.createParser("test_parameter.ffi")
        parser.ffi()

    def testKwargs(self):
        parser = self.createParser("test_kwargs.ffi")
        parser.ffi()

    def testConditions(self):
        parser = self.createParser("test_conditions.ffi")
        parser.ffi()

if __name__ == '__main__':
    unittest.main()

