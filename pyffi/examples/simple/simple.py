import os
from PyFFI import MetaXmlFileFormat
from PyFFI import XmlFileFormat
from PyFFI import Common

class SimpleFormat(XmlFileFormat):
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'simple.xml'
    xmlFilePath = [ os.path.dirname(__file__) ]
    clsFilePath = os.path.dirname(__file__)

    int = Common.Int

