import os
import PyFFI.ObjectModels.XML.FileFormat
import PyFFI.ObjectModels.Common

class _SimpleFormat(PyFFI.ObjectModels.XML.FileFormat.XmlFileFormat):
    xmlFileName = 'simple.xml'
    xmlFilePath = [ os.path.dirname(__file__) ]
    clsFilePath = os.path.dirname(__file__)

    Int = PyFFI.ObjectModels.Common.Int

class SimpleFormat(_SimpleFormat):
    class Example(_SimpleFormat.Example):
        def addInteger(self, x):
            self.numIntegers += 1
            self.integers.updateSize()
            self.integers[self.numIntegers-1] = x
