from FileFormat.XmlFileFormat import MetaXmlFileFormat

class NifFormat(object):
    __metaclass__ = MetaXmlFileFormat
    xmlFileName = 'nif.xml'
    
    def versionNumber(self, version_str):
        v = version_str.split('.')
        num = 0
        shift = 24
        for x in v:
            num += int(x) << shift
            shift -= 8
        return num
