"""
PyFFI provides a metaclass for parsing a file format description 
in XML format.

Using PyFFI
===========

If you simply wish to use PyFFI with a format that's already implemented,
refer to the documentation of that library. For the nif format, refer to
L{PyFFI.NIF}, and for the cgf format, refer to L{PyFFI.CGF}.

Supporting New File Formats
===========================

This section tries to explain how you can implement your own format in PyFFI.

Getting Started
---------------

Suppose you have a simple file format, which consists of an integer, followed
by a list of integers as many as described by the first integer. We start
by creating an XML file, call it simple.xml, which describes this format
in a way that PyFFI can understand::

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE fileformat>
    <fileformat version="1.0">
        <basic name="int">A signed 32-bit integer.</basic>
        <struct name="Example">
            <add name="Num Integers" type="int">
                Number of integers that follow.
            </add>
            <add name="Integers" type="int" arr1="Num Integers">
                A list of integers.
            </add>
        </struct>
    </fileformat>

What PyFFI does is convert this simple XML description into Python classes
which automatically can read and write the structure you've just described.
Say this is the contents of simple.py::

    from PyFFI import MetaXmlFileFormat
    from PyFFI import Common
    class SimpleFormat:
        __metaclass__ = MetaXmlFileFormat
        xmlFileName = 'simple.xml'
        xmlFilePath = [ os.path.dirname(__file__) ]
        clsFilePath = os.path.dirname(__file__)

        int = Common.Int

What happens in this piece of code?

  - The metaclass assignment triggers the transformation of xml into Python
    classes; how these classes can be used will be explained further.
  - The xmlFileName class attribute provides the name of the xml file that
    describes the structures we wish to generate. The xmlFilePath attribute
    gives a list of locations of where to look for this file; in our case we
    have simply chosen to put 'simple.xml' in the same directory as
    'simple.py'.
  - The clsFilePath attribute tells PyFFI where to look for class customizers.
    For instance, we could have another file called Example.py::

        def addInteger(self, x):
            self.numIntegers += 1
            self.integers.updateSize()
            self.integers[self.numIntegers-1] = x

    which would provide the class SimpleFormat.Example with a function
    C{addInteger} in addition to the attributes C{numIntegers} and C{integers}
    which have been created from the XML.
  - Finally, the PyFFI.Common module implements the most common basic types,
    such as integers, characters, and floats. In the above example we have
    taken advantage of Common.Int, which defines a signed 32-bit integer,
    exactly the type we need.

Reading and Writing Files
-------------------------

To read and print the contents of a file of the format described by
simple.xml::

    from simple import SimpleFormat
    x = SimpleFormat.Simple()
    f = open('somefile.simple', 'rb')
    x.read(f)
    f.close()
    print x

Or, to create a new file in this format::

    from simple import SimpleFormat
    x = SimpleFormat.Simple()
    x.numIntegers = 5
    x.integers.updateSize()
    x.integers[0] = 3
    x.integers[1] = 1
    x.integers[2] = 4
    x.integers[3] = 1
    x.integers[4] = 5
    f = open('pi.simple', 'wb')
    x.write(f)
    f.close()

Further References
------------------

With the above simple example in mind, you may wish to browse through the
source code of
L{PyFFI.CGF} or L{PyFFI.NIF} to see how PyFFI works for more complex file
formats.
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, Python File Format Interface
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
# ***** END LICENCE BLOCK *****

__all__ = [ 'XmlHandler', 'Utils', 'Common', 'Bases' ]

__version__ = '0.7.3'

from XmlHandler import XmlSaxHandler

import xml.sax
import os.path

class MetaXmlFileFormat(type):
    """The MetaXmlFileFormat metaclass transforms the XML description of a
    file format into a bunch of classes which can be directly used to
    manipulate files in this format.

    With PyFFI, a file format is implemented as a particular class with
    subclasses corresponding to different (bit)struct types,
    enum types, basic types, and aliases. See NifFormat.py for an example
    of how to use MetaXmlFileFormat.

    The actual implementation of the parser is delegated to PyFFI.XmlHandler.
    """
    
    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare NifFormat to have metaclass
        MetaXmlFileFormat, so upon creation of the NifFormat class,
        the __init__ function is called, with
    
        @param cls: The class created using MetaXmlFileFormat, for example
            NifFormat.
        @param name: The name of the class, for example 'NifFormat'.
        @param bases: The base classes, usually (object,).
        @param dct: A dictionary of class attributes, such as 'xmlFileName'.
        """

        # consistency checks
        if not dct.has_key('xmlFileName'):
            raise TypeError("class %s : missing xmlFileName attribute"%cls)
        if not dct.has_key('versionNumber'):
            raise TypeError("class %s : missing versionNumber attribute"%cls)

        # set up XML parser
        parser = xml.sax.make_parser()
        parser.setContentHandler(XmlSaxHandler(cls, name, bases, dct))

        # open XML file
        if not dct.has_key('xmlFilePath'):
            xmlfile = open(dct['xmlFileName'])
        else:
            for filepath in dct['xmlFilePath']:
                if not filepath:
                    continue
                try:
                    xmlfile = open(os.path.join(filepath, dct['xmlFileName']))
                except IOError:
                    continue
                break
            else:
                raise IOError("'%s' not found in any of the directories %s"%(
                    dct['xmlFileName'], dct['xmlFilePath']))

        # parse the XML file: control is now passed on to XmlSaxHandler
        # which takes care of the class creation
        try:
            parser.parse(xmlfile)
        finally:
            xmlfile.close()
