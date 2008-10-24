"""Base classes for file format descriptions."""

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

from PyFFI import Utils

class MetaFileFormat(type):
    """The MetaFileFormat metaclass is an abstract base class for transforming
    a file format description into classes which can be directly used to
    manipulate files in this format.

    A file format is implemented as a particular class (a subclass of
    L{FileFormat}) with class members corresponding to different
    (bit)struct types, enum types, basic types, and aliases.
    """
    pass

class FileFormat(object):
    """This class can be used as a base class for file formats. It implements
    a number of useful functions such as walking over directory trees and a
    default attribute naming function.
    """

    # override this with a regular expression for the file extension of
    # the format you are implementing
    re_filename = None

    @staticmethod
    def versionNumber(version_str):
        """Converts version string into an integer.
        This default implementation simply returns zero at all times,
        and works for formats that are not versioned.

        Override for versioned formats.

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

        @todo: The plan is eventually to use the L{Data} class for this.
        """
        raise NotImplementedError

    @staticmethod
    def nameAttribute(name):
        """Converts an attribute name, as in the description file,
        into a name usable by python.

        @param name: The attribute name.
        @type name: str
        @return: Reformatted attribute name, useable by python.

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

        @todo: The plan is eventually to use the L{Data} class for this.
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

        @todo: The plan is eventually to use the L{Data} class for this.
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

        @todo: Eventually this will be superseded by L{walkData}.
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

        @todo: Eventually this will be superseded by L{walkData}.
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
                        print("user version 0x%08X" % user_version)
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
                        # corrupt, or that the description is corrupt
                        if verbose >= 1:
                            print("""\
Warning: read failed due corrupt file, corrupt format description, or bug.""")
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
    def walkData(cls, top, topdown=True, verbose=0, mode='rb'):
        """A generator which yields the data of all files in
        directory top whose filename matches the regular expression
        cls.re_filename. The argument top can also be a file instead of a
        directory. Errors coming from os.walk are ignored.

        Note that the caller is not responsible for closing the stream.

        This function is for instance used by L{PyFFI.Spells} to implement
        modifying a file after reading and parsing.

        @param top: The top folder.
        @type top: C{str}
        @param topdown: Determines whether subdirectories should be iterated
            over first.
        @type topdown: C{bool}
        @param verbose: Verbosity level.
        @type verbose: C{int}
        @param mode: The mode in which to open files.
        @type mode: C{str}

        @status: Not yet functional. For the time being, fall back on the other
            walk functions.
        """
        # now walk over all these files in directory top
        for filename in Utils.walk(top, topdown, onerror = None,
                                   re_filename = cls.re_filename):
            if verbose >= 1:
                print("reading %s" % filename)
            stream = open(filename, mode)
            try:
                try:
                    # return data for the stream
                    # the caller can call data.read(stream),
                    # or data.inspect(stream), etc.
                    data = cls.Data()
                    yield stream, data
                except StandardError:
                    # an error occurred during reading or inspecting
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
        """Returns list of all root blocks. Used by L{PyFFI.QSkope}
        and L{PyFFI.Spells}.

        @param readresult: Result from L{walk} or L{read}.
        @type readresult: tuple
        @return: list of root blocks

        @todo: The plan is eventually to use the L{Data} class for this.
        """
        return []

    @classmethod
    def getBlocks(cls, *readresult):
        """Returns list of all blocks. Used by L{PyFFI.QSkope}
        and L{PyFFI.Spells}.

        @param readresult: Result from L{walk} or L{read}.
        @type readresult: tuple
        @return: list of blocks

        @todo: The plan is eventually to use the L{Data} class for this.
        """
        return []

