"""This module implements the DAE file format. Not yet functional.

Examples
========

Read a DAE file
---------------

>>> # check and read dae file
>>> stream = open('tests/dae/cube.dae', 'rb')
>>> root = DaeFormat.read(stream)
>>> # print DAE file
>>> #print root
>>> stream.close()

Parse all DAE files in a directory tree
---------------------------------------

>>> for root in DaeFormat.walk('tests/dae',
...                            raisereaderror = True,
...                            verbose = 1):
...     pass
reading tests/dae/cube.dae

Create a DAE file from scratch and write to file
------------------------------------------------

>>> root = None #DaeFormat.Root()
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> DaeFormat.write(stream, root)
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

import struct
import os
import re

from PyFFI.XsdFormat import XsdFileFormat
from PyFFI.XsdFormat import MetaXsdFileFormat

class DaeFormat(XsdFileFormat):
    """This class implements the DAE format."""
    __metaclass__ = MetaXsdFileFormat
    xsdFileName = 'COLLADASchema.xsd'
    # where to look for the xsd file and in what order:
    # DAEXSDPATH env var, or XsdFormat module directory
    xsdFilePath = [os.getenv('DAEXSDPATH'), os.path.dirname(__file__)]
    # path of class customizers
    clsFilePath = os.path.dirname(__file__)
    # file name regular expression match
    re_filename = re.compile(r'^.*\.dae$', re.IGNORECASE)
    # used for comparing floats
    _EPSILON = 0.0001

    # basic types
    # TODO

    # implementation of dae-specific basic types
    # TODO

    # exceptions
    class DaeError(StandardError):
        """Exception class used for DAE related exceptions."""
        pass

