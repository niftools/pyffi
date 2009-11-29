import os
import pyffi.object_models.xml
import pyffi.object_models.common

class SimpleFormat(pyffi.object_models.xml.FileFormat):
    xml_file_name = 'simple.xml'
    xml_file_path = [ os.path.dirname(__file__) ]

    # basic types

    Int = pyffi.object_models.common.Int

    # extensions of generated types

    class Example:
        def addInteger(self, x):
            self.numIntegers += 1
            self.integers.update_size()
            self.integers[self.numIntegers-1] = x
