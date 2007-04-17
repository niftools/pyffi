from XmlHandler import XmlHandler

class MetaXmlFileFormat(type):
    """The MetaXmlFileFormat metaclass transforms the XML description of a
    file format into a bunch of classes which can be directly used to
    manipulate files in this format.

    In particular, a file format corresponds to a particular class with
    subclasses corresponding to different file block types, compound
    types, enum types, and basic types. See NifFormat.py for an example
    of how to use MetaXmlFileFormat.
    """
    
    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare NifFormat to have metaclass
        MetaXmlFileFormat, so upon creation of the NifFormat class,
        the __init__ function is called, with
    
        cls   : NifFormat
        name  : 'NifFormat'
        bases : a tuple (object,) since NifFormat is derived from object
        dct   : dictionary of NifFormat attributes, such as 'xmlFileName'
        """

        # consistency checks
        if not dct.has_key('xmlFileName'):
            raise TypeError("class " + str(cls) + " : missing xmlFileName attribute")
        if not dct.has_key('versionNumer'):
            raise TypeError("class " + str(cls) + " : missing versionNumber attribute")

        # set up XML parser
        parser = xml.sax.make_parser()
        parser.setContentHandler(XmlHandler(cls, name, bases, dct))

        # parse the XML file: control is now passed on to XmlHandler
        # which takes care of the class creation
        parser.parse(dct['xmlFileName'])
