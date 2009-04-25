import os
import PyFFI.ObjectModels.XML.FileFormat
import PyFFI.ObjectModels.Common

class SimpleFormat(PyFFI.ObjectModels.XML.FileFormat.XmlFileFormat):
    xmlFileName = 'simple.xml'
    xmlFilePath = [ os.path.dirname(__file__) ]
    clsFilePath = os.path.dirname(__file__)

    Int = PyFFI.ObjectModels.Common.Int

    class Example:
        def addInteger(self, x):
            self.numIntegers += 1
            self.integers.updateSize()
            self.integers[self.numIntegers-1] = x
