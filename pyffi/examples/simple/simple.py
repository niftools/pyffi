import os
from PyFFI.ObjectModels.XML.FileFormat import MetaXmlFileFormat
from PyFFI.ObjectModels.XML.FileFormat import XmlFileFormat
from PyFFI import Common

class SimpleFormat(XmlFileFormat):
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'simple.xml'
    xmlFilePath = [ os.path.dirname(__file__) ]
    clsFilePath = os.path.dirname(__file__)

    int = Common.Int

