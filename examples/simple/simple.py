import os
import PyFFI.ObjectModels.xml
import PyFFI.ObjectModels.Common

class SimpleFormat(PyFFI.ObjectModels.xml.FileFormat):
    xmlFileName = 'simple.xml'
    xmlFilePath = [ os.path.dirname(__file__) ]

    # basic types

    Int = PyFFI.ObjectModels.Common.Int

    # extensions of generated types

    class Example:
        def addInteger(self, x):
            self.numIntegers += 1
            self.integers.updateSize()
            self.integers[self.numIntegers-1] = x
