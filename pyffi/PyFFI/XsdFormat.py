"""This module provides a base class and a metaclass for parsing an XSD
schema and providing an interface for writing XML files that follow this
schema.
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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

from PyFFI.XsdHandler import XsdSaxHandler
from PyFFI import Utils

import xml.sax
import os.path

class MetaXsdFileFormat(type):
    """The MetaXsdFileFormat metaclass transforms the XSD description of a
    xml format into a bunch of classes which can be directly used to
    manipulate files in this format.

    The actual implementation of the parser is delegated to
    L{PyFFI.XsdHandler}.
    """

    def __init__(cls, name, bases, dct):
        """This function constitutes the core of the class generation
        process. For instance, we declare DaeFormat to have metaclass
        MetaXsdFileFormat, so upon creation of the DaeFormat class,
        the __init__ function is called, with

        @param cls: The class created using MetaXsdFileFormat, for example
            DaeFormat.
        @param name: The name of the class, for example 'DaeFormat'.
        @param bases: The base classes, usually (object,).
        @param dct: A dictionary of class attributes, such as 'xsdFileName'.
        """
        super(MetaXsdFileFormat, cls).__init__(name, bases, dct)

        # consistency checks
        if not 'xsdFileName' in dct:
            raise TypeError("class %s : missing xsdFileName attribute" % cls)

        # set up XML parser
        parser = xml.sax.make_parser()
        parser.setContentHandler(XsdSaxHandler(cls, name, bases, dct))

        # open XSD file
        if not 'xsdFilePath' in dct:
            xsdfile = open(dct['xsdFileName'])
        else:
            for filepath in dct['xsdFilePath']:
                if not filepath:
                    continue
                try:
                    xsdfile = open(os.path.join(filepath, dct['xsdFileName']))
                except IOError:
                    continue
                break
            else:
                raise IOError("'%s' not found in any of the directories %s"%(
                    dct['xsdFileName'], dct['xsdFilePath']))

        # parse the XSD file: control is now passed on to XsdSaxHandler
        # which takes care of the class creation
        try:
            parser.parse(xsdfile)
        finally:
            xsdfile.close()

class XsdFileFormat(object):
    """This class can be used as a base class for file formats. It implements
    a number of useful functions such as walking over directory trees and a
    default attribute naming function.
    """

    # override this with a regular expression for the file extension of
    # the format you are implementing
    re_filename = None

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xsd file, into a name usable
        by python.

        @param name: The attribute name.
        @type name: str
        @return: Reformatted attribute name, useable by python.

        >>> XsdFileFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """

        # str(name) converts name to string in case name is a unicode string
        parts = str(name).split()
        return "_".join(part.lower() for part in parts)

    @staticmethod
    def nameClass(name):
        """Converts a class name, as in the xsd file, into a name usable
        by python.

        @param name: The class name.
        @type name: str
        @return: Reformatted class name, useable by python.

        >>> XsdFileFormat.nameClass('tHis is A Silly naME')
        'ThisIsASillyName'
        """

        # str(name) converts name to string in case name is a unicode string
        partss = [part.split("_") for part in str(name).split()]
        attrname = ""
        for parts in partss:
            for part in parts:
                attrname += part.capitalize()
        return attrname

    @classmethod
    def read(cls, stream):
        """Read a file.

        @param stream: The stream from which to read.
        @type stream: file
        @return: The root of the DOM tree.
        """
        return None
        #raise NotImplementedError

    @classmethod
    def write(cls, stream, root):
        """Write a file.

        @param stream: The stream to which to write.
        @type stream: file
        @param root: The root of the DOM tree.
        @type root: ???
        """
        return None
        #raise NotImplementedError

    @classmethod
    def walk(cls, top, topdown = True, raisereaderror = False, verbose = 0):
        """A generator which yields the cls.read result of all files in
        directory top whose filename matches the regular expression
        cls.re_filename. The argument top can also be a file instead of a
        directory. Errors coming from os.walk are ignored.

        @param top: The top folder.
        @type top: str
        @param topdown: Determines whether subdirectories should be iterated
            over first.
        @type topdown: bool
        @param raisereaderror: Should read errors raise an exception, or
            should they be ignored?
        @type raisereaderror: bool
        @param verbose: Verbosity level.
        @type verbose: int
        """
        for result in cls.walkFile(
            top, topdown = topdown,
            raisereaderror = raisereaderror, verbose = verbose):
            # discard first item from result (stream)
            yield result[1:]

    @classmethod
    def walkFile(cls, top, topdown = True,
                 raisereaderror = False, verbose = 0, mode = 'rb'):
        """Like L{walk}, but returns more information: stream, root.

        Note that the caller is not responsible for closing stream.

        This function is for instance used by L{PyFFI.Spells} to implement
        modifying a file after reading and parsing.

        @param top: The top folder.
        @type top: str
        @param topdown: Determines whether subdirectories should be iterated
            over first.
        @type topdown: bool
        @param raisereaderror: Should read errors raise an exception, or
            should they be ignored?
        @type raisereaderror: bool
        @param verbose: Verbosity level.
        @type verbose: int
        """
        # now walk over all these files in directory top
        for filename in Utils.walk(top, topdown, onerror = None,
                                   re_filename = cls.re_filename):
            if verbose >= 1:
                print("reading %s" % filename)
            stream = open(filename, mode)
            try:
                try:
                    # return (version, stream) + result of read
                    root = cls.read(stream)
                    yield stream, root
                except StandardError:
                    # an error occurred during reading
                    # this should not happen: means that the file is
                    # corrupt, or that the xsd is corrupt
                    if verbose >= 1:
                        print("""\
Warning: read failed due to either a corrupt file, a corrupt xsd, or a bug.""")
                    if verbose >= 2:
                        Utils.hexDump(stream)
                    if raisereaderror:
                        raise
            finally:
                stream.close()

    @classmethod
    def getRoots(cls, *readresult):
        """Returns list of all root blocks. Used by L{PyFFI.QSkopeLib.QSkope}
        and L{PyFFI.Spells}.

        @param readresult: Result from L{walk} or L{read}.
        @type readresult: tuple
        @return: list of root blocks
        """
        return []

    @classmethod
    def getBlocks(cls, *readresult):
        """Returns list of all blocks. Used by L{PyFFI.QSkopeLib.QSkope}
        and L{PyFFI.Spells}.

        @param readresult: Result from L{walk} or L{read}.
        @type readresult: tuple
        @return: list of blocks
        """
        return []

