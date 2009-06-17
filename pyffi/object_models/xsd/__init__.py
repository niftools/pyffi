"""This module provides a base class and a metaclass for parsing an XSD
schema and providing an interface for writing XML files that follow this
schema.
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import logging
import time
import weakref
import xml.etree.cElementTree

import pyffi.object_models

class Tree(object):
    """Converts an xsd element tree into a tree of nodes that contain
    all information and methods for creating classes. Each node has a
    class matching the element type. The node constructor
    :meth:`Node.__init__` extracts the required information from the
    element and its children, thereby constructing the tree of nodes.
    Once the tree is constructed, call the :meth:`Node.class_factory`
    method to get a list of classes.
    """

    logger = logging.getLogger("pyffi.object_models.xsd")
    """For logging debug messages, warnings, and errors."""

    class Node(object):
        """Base class for all nodes in the tree."""

        schema = None
        """A weak reference to the root element of the tree."""

        parent = None
        """A weak reference to the parent element of this node, or None."""

        children = None
        """The child elements of this node."""

        def __init__(self, element, parent):
            # note: using weak references to avoid reference cycles
            self.parent = weakref.proxy(parent) if parent else None
            self.schema = self.parent.schema if parent else weakref.proxy(self)

            # create nodes for all children
            self.children = [Tree.node_factory(child, self)
                             for child in element.getchildren()]

        # note: this corresponds roughly to the 'clsFor' method in pyxsd
        def class_factory(self):
            """Generator which yields all classes for the schema."""
            for child in self.children:
                for class_ in child.class_factory():
                    yield class_

    class All(Node):
        pass

    class Annotation(Node):
        pass

    class Any(Node):
        pass

    class AnyAttribute(Node):
        pass

    class Appinfo(Node):
        pass

    class Attribute(Node):
        pass

    class AttributeGroup(Node):
        pass

    class Choice(Node):
        pass

    class ComplexContent(Node):
        pass

    ##http://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html#element-complexType
    ##<complexType
    ##  abstract = boolean : false
    ##  block = (#all | List of (extension | restriction))
    ##  final = (#all | List of (extension | restriction))
    ##  id = ID
    ##  mixed = boolean : false
    ##  name = NCName
    ##  {any attributes with non-schema namespace . . .}>
    ##  Content: (annotation?, (simpleContent | complexContent | ((group | all | choice | sequence)?, ((attribute | attributeGroup)*, anyAttribute?))))
    ##</complexType>
    class ComplexType(Node):
        name = None
        """The name of the type."""

        def __init__(self, element, parent):
            Tree.Node.__init__(self, element, parent)
            self.name = element.get("name")

        def class_factory(self):
            # construct a class name
            if self.name:
                class_name = self.name
            elif isinstance(self.parent, Tree.Element):
                # find element that contains this type
                class_name = self.parent.name
            # XXX todo: filter class name so it conforms naming conventions
            if not class_name:
                raise ValueError("Failed to find class name for complexType.")
            # construct bases
            class_bases = (object,)
            # construct class dictionary
            class_dict = {}
            class_dict["_node"] = self
            # create class
            class_ = type(class_name, class_bases, class_dict)
            # assign child classes
            for child_class in Tree.Node.class_factory(self):
                setattr(class_, child_class.__name__, child_class)
            # yield the generated class
            yield class_

    class Documentation(Node):
        pass

    ##http://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html#element-element
    ##<element
    ##  abstract = boolean : false
    ##  block = (#all | List of (extension | restriction | substitution))
    ##  default = string
    ##  final = (#all | List of (extension | restriction))
    ##  fixed = string
    ##  form = (qualified | unqualified)
    ##  id = ID
    ##  maxOccurs = (nonNegativeInteger | unbounded)  : 1
    ##  minOccurs = nonNegativeInteger : 1
    ##  name = NCName
    ##  nillable = boolean : false
    ##  ref = QName
    ##  substitutionGroup = QName
    ##  type = QName
    ##  {any attributes with non-schema namespace . . .}>
    ##  Content: (annotation?, ((simpleType | complexType)?, (unique | key | keyref)*))
    ##</element>
    class Element(Node):
        name = None
        """The name of the element."""

        ref = None
        """If the element is declared elsewhere, then this contains the name
        of the reference.
        """

        type_ = None
        """The type of the element. This determines which attributes,
        elements, and content, this element can have.
        """

        def __init__(self, element, parent):
            Tree.Node.__init__(self, element, parent)
            self.name = element.get("name")
            self.ref = element.get("ref")
            self.type_ = element.get("type")
            if (not self.name) and (not self.ref):
                raise ValueError("Element %s has neither name nor ref."
                                 % element)

    class Enumeration(Node):
        pass

    class Extension(Node):
        pass

    class Field(Node):
        pass

    class Group(Node):
        pass

    class Import(Node):
        pass

    class Include(Node):
        pass

    class Key(Node):
        pass

    class Keyref(Node):
        pass

    class Length(Node):
        pass

    class List(Node):
        pass

    class MaxExclusive(Node):
        pass

    class MaxInclusive(Node):
        pass

    class MaxLength(Node):
        pass

    class MinInclusive(Node):
        pass

    class MinLength(Node):
        pass

    class Pattern(Node):
        pass

    class Redefine(Node):
        pass

    class Restriction(Node):
        pass

    ##http://www.w3.org/TR/2004/REC-xmlschema-1-20041028/structures.html#element-schema
    ##<schema
    ##  attributeFormDefault = (qualified | unqualified) : unqualified
    ##  blockDefault = (#all | List of (extension | restriction | substitution))  : ''
    ##  elementFormDefault = (qualified | unqualified) : unqualified
    ##  finalDefault = (#all | List of (extension | restriction | list | union))  : ''
    ##  id = ID
    ##  targetNamespace = anyURI
    ##  version = token
    ##  xml:lang = language
    ##  {any attributes with non-schema namespace . . .}>
    ##  Content: ((include | import | redefine | annotation)*, (((simpleType | complexType | group | attributeGroup) | element | attribute | notation), annotation*)*)
    ##</schema>
    class Schema(Node):
        """Class wrapper for schema tag."""

        version = None
        """Version attribute."""

        def __init__(self, element, parent):
            if parent is not None:
                raise ValueError("Schema can only occur as root element.")
            Tree.Node.__init__(self, element, parent)
            self.version = element.get("version")

    class Selector(Node):
        pass
        
    class Sequence(Node):
        pass

    class SimpleContent(Node):
        pass

    class SimpleType(Node):
        pass

    class Union(Node):
        pass

    class Unique(Node):
        pass

    @classmethod
    # note: this corresponds to the 'factory' method in pyxsd
    def node_factory(cls, element, parent):
        """Create an appropriate instance for the given xsd element."""
        # get last part of the tag
        class_name = element.tag.split("}")[-1]
        class_name = class_name[0].upper() + class_name[1:]
        try:
            return getattr(cls, class_name)(element, parent)
        except AttributeError:
            cls.logger.warn("Unknown element type: making dummy node class %s."
                            % class_name)
            class_ = type(class_name, (cls.Node,), {})
            setattr(cls, class_name, class_)
            return class_(element, parent)

class MetaFileFormat(pyffi.object_models.MetaFileFormat):
    """The MetaFileFormat metaclass transforms the XSD description of a
    xml format into a bunch of classes which can be directly used to
    manipulate files in this format.

    The actual implementation of the parser is delegated to
    :class:`Tree`.
    """

    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare DaeFormat to have metaclass
        MetaFileFormat, so upon creation of the DaeFormat class,
        the __init__ function is called, with

        :param cls: The class created using MetaFileFormat, for example
            DaeFormat.
        :param name: The name of the class, for example 'DaeFormat'.
        :param bases: The base classes, usually (object,).
        :param dct: A dictionary of class attributes, such as 'xsdFileName'.
        """
        super(MetaFileFormat, cls).__init__(name, bases, dct)

        # open XSD file
        xsdfilename = dct.get('xsdFileName')
        if xsdfilename:
            # open XSD file
            xsdfile = cls.openfile(xsdfilename, cls.xsdFilePath)

            # parse the XSD file
            cls.logger.debug("Parsing %s and generating classes." % xsdfilename)
            start = time.clock()
            try:
                # create nodes for every element in the XSD tree
                schema = Tree.node_factory(
                    xml.etree.cElementTree.parse(xsdfile).getroot(),
                    None)
            finally:
                xsdfile.close()
            # generate classes
            for class_ in schema.class_factory():
                setattr(cls, class_.__name__, class_)
            cls.logger.debug("Parsing finished in %.3f seconds."
                             % (time.clock() - start))

class FileFormat(pyffi.object_models.FileFormat):
    """This class can be used as a base class for file formats. It implements
    a number of useful functions such as walking over directory trees and a
    default attribute naming function.
    """
    __metaclass__ = MetaFileFormat
    xsdFileName = None #: Override.
    xsdFilePath = None #: Override.
    logger = logging.getLogger("pyffi.object_models.xsd")

    @staticmethod
    def name_attribute(name):
        """Converts an attribute name, as in the xsd file, into a name usable
        by python.

        :param name: The attribute name.
        :type name: str
        :return: Reformatted attribute name, useable by python.

        >>> FileFormat.name_attribute('tHis is A Silly naME')
        'this_is_a_silly_name'
        """

        # str(name) converts name to string in case name is a unicode string
        parts = str(name).replace(":", "_").split()
        return "_".join(part.lower() for part in parts)

    @staticmethod
    def name_class(name):
        """Converts a class name, as in the xsd file, into a name usable
        by python.

        :param name: The class name.
        :type name: str
        :return: Reformatted class name, useable by python.

        >>> FileFormat.name_class('this IS a sillyNAME')
        'ThisISASillyNAME'
        """

        # str(name) converts name to string in case name is a unicode string
        partss = [part.split("_") for part in str(name).split()]
        attrname = ""
        for parts in partss:
            for part in parts:
                attrname += part[0].upper() + part[1:]
        return attrname
