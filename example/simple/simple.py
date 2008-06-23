import os
from PyFFI import MetaXmlFileFormat
from PyFFI import Common
class SimpleFormat:
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'simple.xml'
    xmlFilePath = [ os.path.dirname(__file__) ]
    clsFilePath = os.path.dirname(__file__)

    int = Common.Int

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into version integer."""
        return 0

    @staticmethod
    def nameAttribute(name):
        """Converts xml attribute name into a name usable by python."""
        parts = str(name).replace("?", "X").split() # str(name) converts name to string in case name is a unicode string
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname
