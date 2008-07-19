"""Defines abstract base class for any type that stores data which is
readable and writable. This base class also defines a special function
which generates immutable objects that can be used to identify the object.
"""

# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------

class AnyType(object):
    """Abstract base class from which all complex types are derived."""

    def read(self, stream, **kwargs):
        """Read object from file.

        @param stream: The stream to read from.
        @type stream: file
        """
        raise NotImplementedError

    def write(self, stream, **kwargs):
        """Write object to file.

        @param stream: The stream to write to.
        @type stream: file
        """
        raise NotImplementedError

    def identityGenerator(self, **kwargs):
        """Returns a generator which yields a sequence of integers,
        such that objects which are "close" to each other, or
        which can be considered equal for practical purposes, yield
        the same sequence. This is useful for instance when comparing
        data and trying to remove duplicates.

        This function returns a generator so not all of the data needs to
        be parsed in order to determine non-equality.

        @return: A generator for immutable objects.
        """
        raise NotImplementedError

    def __eq__(self, other):
        """Check equality, using L{identityGenerator}. Do not override this
        function. Instead, override L{identityGenerator}.

        @param other: The object to compare with.
        @type other: L{AnyType}
        @return: C{True} if equal, C{False} otherwise
        """
        # type check
        if not isinstance(other, AnyType):
            raise TypeError("cannot compare %s and %s"
                            % (self.__class__.__name__,
                               other.__class__.__name__))
        # compare generator results
        self_idgen = self.identityGenerator()
        other_idgen = other.identityGenerator()
        for self_id in self_idgen:
            try:
                other_id = other_idgen.next()
            except StopIteration:
                # other has less data
                return False
            if self_id != other_id:
                return False
        # check that other generator is done as well
        try:
            other_idgen.next()
        except StopIteration:
            return True
        else:
            # other has trailing data
            return False

    def __neq__(self, other):
        """Check inequality, using L{identityGenerator}.

        @param other: The object to compare with.
        @type other: L{AnyType}
        @return: C{False} if equal, C{True} otherwise
        """
        return not self.__eq__(other)

