"""
PyFFI provides a metaclass for parsing a file format description in XML format.
The actual implementation of the parser is delegated to PyFFI.XmlHandler.
The most common basic types are implemented in PyFFI.Common.
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

__version__ = '0.3.3'

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
    """
    
    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare NifFormat to have metaclass
        MetaXmlFileFormat, so upon creation of the NifFormat class,
        the __init__ function is called, with
    
        @param cls: the class created using MetaXmlFileFormat, for example NifFormat
        @param name: the name of the class, for example 'NifFormat'
        @param bases: the base classes, usually (object,)
        @param dct: dictionary of class attributes, such as 'xmlFileName'
        """

        # consistency checks
        if not dct.has_key('xmlFileName'):
            raise TypeError("class " + str(cls) + " : missing xmlFileName attribute")
        if not dct.has_key('versionNumber'):
            raise TypeError("class " + str(cls) + " : missing versionNumber attribute")

        # set up XML parser
        parser = xml.sax.make_parser()
        parser.setContentHandler(XmlSaxHandler(cls, name, bases, dct))

        # open XML file
        if not dct.has_key('xmlFilePath'):
            f = open(dct['xmlFileName'])
        else:
            for p in dct['xmlFilePath']:
                if not p: continue
                try:
                    f = open(os.path.join(p, dct['xmlFileName']))
                except IOError:
                    continue
                break
            else:
                raise IOError("'%s' not found in any of the directories %s"%(dct['xmlFileName'], dct['xmlFilePath']))

        # parse the XML file: control is now passed on to XmlSaxHandler
        # which takes care of the class creation
        try:
            parser.parse(f)
        finally:
            f.close()
