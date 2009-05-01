import os
import PyFFI.object_models.xml
import PyFFI.object_models.Common

class SimpleFormat(PyFFI.object_models.xml.FileFormat):
    xmlFileName = 'simple.xml'
    xmlFilePath = [ os.path.dirname(__file__) ]

    # basic types

    Int = PyFFI.object_models.Common.Int

    # extensions of generated types

    class Example:
        def addInteger(self, x):
            self.numIntegers += 1
            self.integers.updateSize()
            self.integers[self.numIntegers-1] = x
