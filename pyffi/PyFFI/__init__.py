"""
PyFFI provides a metaclass for parsing a file format description
in XML format.

Using PyFFI
===========

If you simply wish to use PyFFI with a format that's already implemented,
refer to the documentation of that library:
  - L{PyFFI.Formats.NIF}
  - L{PyFFI.Formats.KFM}
  - L{PyFFI.Formats.CGF}
  - L{PyFFI.Formats.DDS}
  - L{PyFFI.Formats.TGA}

Supporting New File Formats
===========================

This section tries to explain how you can implement your own format in PyFFI.

Getting Started
---------------

Note that the files which make up the following example can all be found in
the examples/simple directory of the source distribution of PyFFI.

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
            return 0

        @staticmethod
        def nameAttribute(name):
            parts = str(name).split() # str(name) converts unicode to str
            attrname = parts[0].lower()
            for part in parts[1:]:
                attrname += part.capitalize()
            return attrname

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
  - The versionNumber function is useful for implementing file formats that
    have different versions, and converts the xml version strings into Python
    integers. As this feature is not used in this simple example, it simply
    returns zero.
  - The nameAttribute function converts attribute names as specified in the
    xml into Python attribute names. This implementation simply removes spaces
    and uses a default capitalization.

Reading and Writing Files
-------------------------

To read and print the contents of a file of the format described by
simple.xml::

    from simple import SimpleFormat
    x = SimpleFormat.Example()
    f = open('somefile.simple', 'rb')
    x.read(f)
    f.close()
    print x

Or, to create a new file in this format::

    from simple import SimpleFormat
    x = SimpleFormat.Example()
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
L{PyFFI.Formats.CGF} or L{PyFFI.Formats.NIF} to see how PyFFI works for more complex file
formats.
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

__all__ = ['XmlHandler', 'Utils', 'Common', 'Bases']

__version__ = '0.12.0'
__hexversion__ = eval('0x%02X%02X%02X'
                      % tuple(int(x) for x in __version__.split('.')))

from PyFFI.XmlHandler import XmlSaxHandler
from PyFFI import Utils

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
        super(MetaXmlFileFormat, cls).__init__(name, bases, dct)

        # consistency checks
        if not 'xmlFileName' in dct:
            raise TypeError("class %s : missing xmlFileName attribute" % cls)

        # set up XML parser
        parser = xml.sax.make_parser()
        parser.setContentHandler(XmlSaxHandler(cls, name, bases, dct))

        # open XML file
        if not 'xmlFilePath' in dct:
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

class XmlFileFormat(object):
    """This class can be used as a base class for file formats. It implements
    a number of useful functions such as walking over directory trees and a
    default attribute naming function."""

    # override this with a regular expression for the file extension of
    # the format you are implementing
    re_filename = None

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.
        This default implementation simply returns zero at all times,
        and works for formats that are not versioned.

        @param version_str: The version string.
        @type version_str: str
        @return: A version integer.
        """
        return 0

    @classmethod
    def getVersion(cls, stream):
        """Returns version and user version numbers. Override this
        function. When implementing this function, take care to preserve the
        stream position: for instance, start with
        C{pos = stream.tell()} and end with C{stream.seek(pos)}.

        @param stream: The stream from which to read.
        @type stream: file
        @return: The version and user version of the file.
            Returns C{(-1, 0)} if file is of known format but the particular
            version not supported.
            Returns C{(-2, 0)} if format is not known.
        """
        raise NotImplementedError

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the xml file, into a name usable
        by python.

        @param name: The attribute name.
        @type name: str
        @return: Reformatted attribute name, useable by python.

        >>> XmlFileFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """

        # str(name) converts name to string in case name is a unicode string
        parts = str(name).split()
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    @classmethod
    def read(cls, stream, version = None, user_version = None, **kwargs):
        """Read a file. Override this function.

        @param stream: The stream from which to read.
        @type stream: file
        @param version: The version as obtained by L{getVersion}.
        @type version: int
        @param user_version: The user version as obtained by L{getVersion}.
        @type user_version: int
        @param kwargs: Extra keyword arguments.
        @return: A tuple of objects (typically, header, blocks, and footer)
            describing the file.
        """
        raise NotImplementedError

    @classmethod
    def write(cls, stream, version = None, user_version = None, **kwargs):
        """Write a file. Override this function.
        The extra arguments must be organized such that calling
        C{write(stream, version, user_version,
        *read(stream, version, user_version)} would rewrite the original file
        back to the stream as it is.

        @param stream: The stream to which to write.
        @type stream: file
        @param version: The version number.
        @type version: int
        @param user_version: The user version number.
        @type user_version: int
        @param kwargs: Extra keyword arguments (e.g. header, block list, ...)
        """
        raise NotImplementedError

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
            # discard first two items from result (version and stream)
            yield result[3:]

    @classmethod
    def walkFile(cls, top, topdown = True,
                 raisereaderror = False, verbose = 0, mode = 'rb'):
        """Like L{walk}, but returns more information:
        stream, version, user_version, and the result from L{read}.

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
                # get the version and user version
                version, user_version = cls.getVersion(stream)
                if version >= 0:
                    # we got it, so now read the file
                    if verbose >= 2:
                        print("version      0x%08X" % version)
                        print("user version 0x%08X" % version)
                    try:
                        # return (version, stream) + result of read
                        result = cls.read(stream,
                                          version = version,
                                          user_version = user_version)
                        if not isinstance(result, tuple):
                            result = (result,)
                        yield (stream, version, user_version) + result
                    except StandardError:
                        # an error occurred during reading
                        # this should not happen: means that the file is
                        # corrupt, or that the xml is corrupt
                        if verbose >= 1:
                            print("""\
Warning: read failed due to either a corrupt file, a corrupt xml, or a bug.""")
                        if verbose >= 2:
                            Utils.hexDump(stream)
                        if raisereaderror:
                            raise
                # getting version failed, do not raise an exception
                # but tell user what happened
                elif version == -1:
                    if verbose >= 1:
                        print('version not supported')
                else:
                    if verbose >= 1:
                        print('file format not recognized')
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

