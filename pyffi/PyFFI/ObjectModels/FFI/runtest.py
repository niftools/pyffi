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



if __name__ == '__main__':
    unittest.main()

