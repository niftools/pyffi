"""Base classes for file format descriptions."""

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

import os.path # os.path.altsep

import PyFFI.Utils
import PyFFI.ObjectModels.Graph

class MetaFileFormat(type):
    """The MetaFileFormat metaclass is an abstract base class for transforming
    a file format description into classes which can be directly used to
    manipulate files in this format.

    A file format is implemented as a particular class (a subclass of
    :class:`FileFormat`) with class members corresponding to different
    (bit)struct types, enum types, basic types, and aliases.
    """

    @staticmethod
    def openfile(filename, filepaths=None):
        """Find *filename* in given *filepaths*, and open it. Raises IOError if
        file cannot be opened.
        """
        if not filepaths:
            return open(filename)
        else:
            for filepath in filepaths:
                if not filepath:
                    continue
                try:
                    return open(os.path.join(filepath, filename))
                except IOError:
                    continue
                break
            else:
                raise IOError(
                    "'%s' not found in any of the directories %s"
                    % (filename, filepaths))

class FileFormat(object):
    """This class is the base class for all file formats. It implements
    a number of useful functions such as walking over directory trees
    (L{walkData}) and a default attribute naming function (L{nameAttribute}).
    It also implements the base class for representing file data
    (L{FileFormat.Data}).

    @cvar RE_FILENAME: Regular expression for matching filenames of this file
        type.
    :type RE_FILENAME: C{SRE_Pattern} (that is, the result of a C{re.compile}
        call)
    """

    RE_FILENAME = None
    """Override this with a regular expression for the file extension of
    the format you are implementing.
    """

    # override this with the data instance for this format
    class Data(PyFFI.ObjectModels.Graph.GlobalNode):
        """Base class for representing data in a particular format.
        Override this class to implement reading and writing.
        """

        def inspect(self, stream):
            """Quickly checks whether the stream appears to contain
            data of a particular format. Resets stream to original position.
            Call this function if you simply wish to check that a file is
            of a particular format without having to parse it completely.

            Override this method.

            :param stream: The file to inspect.
            :type stream: file
            :return: ``True`` if stream is of particular format, ``False``
                otherwise.
            """
            raise NotImplementedError

        def read(self, stream):
            """Read data of particular format from stream.
            Override this method.

            :param stream: The file to read from.
            :type stream: file
            """
            raise NotImplementedError

        def write(self, stream):
            """Write data of particular format to stream.
            Override this method.

            :param stream: The file to write to.
            :type stream: file
            """
            raise NotImplementedError

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.
        This default implementation simply returns zero at all times,
        and works for formats that are not versioned.

        Override for versioned formats.

        :param version_str: The version string.
        :type version_str: str
        :return: A version integer.
        """
        return 0

    @classmethod
    def getVersion(cls, stream):
        """Returns version and user version numbers. Override this
        function. When implementing this function, take care to preserve the
        stream position: for instance, start with
        C{pos = stream.tell()} and end with C{stream.seek(pos)}.

        :param stream: The stream from which to read.
        :type stream: file
        :return: The version and user version of the file.
            Returns C{(-1, 0)} if file is of known format but the particular
            version not supported.
            Returns C{(-2, 0)} if format is not known.

        @todo: The plan is eventually to use the L{Data} class for this.
        """
        raise NotImplementedError

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the description file,
        into a name usable by python.

        :param name: The attribute name.
        :type name: str
        :return: Reformatted attribute name, useable by python.

        >>> FileFormat.nameAttribute('tHis is A Silly naME')
        'thisIsASillyName'
        """

        # str(name) converts name to string in case name is a unicode string
        parts = str(name).split()
        attrname = parts[0].lower()
        for part in parts[1:]:
            attrname += part.capitalize()
        return attrname

    # TODO: port nameClass(name) from XsdFileFormat

    @classmethod
    def walkData(cls, top, topdown=True, mode='rb'):
        """A generator which yields the data of all files in
        directory top whose filename matches the regular expression
        L{RE_FILENAME}. The argument top can also be a file instead of a
        directory. Errors coming from os.walk are ignored.

        Note that the caller is not responsible for closing the stream.

        This function is for instance used by L{PyFFI.Spells} to implement
        modifying a file after reading and parsing.

        :param top: The top folder.
        :type top: ``str``
        :param topdown: Determines whether subdirectories should be iterated
            over first.
        :type topdown: ``bool``
        :param mode: The mode in which to open files.
        :type mode: ``str``
        """
        # now walk over all these files in directory top
        for filename in PyFFI.Utils.walk(top, topdown, onerror=None,
                                         re_filename=cls.RE_FILENAME):
            stream = open(filename, mode)
            try:
                # return data for the stream
                # the caller can call data.read(stream),
                # or data.inspect(stream), etc.
                data = cls.Data()
                yield stream, data
            finally:
                stream.close()
