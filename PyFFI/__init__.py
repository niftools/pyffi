"""
Supported File Formats
----------------------

If you simply wish to use PyFFI with a format that's already implemented,
refer to the documentation of that library:

* :mod:`PyFFI.Formats.NIF`
* :mod:`PyFFI.Formats.KFM`
* :mod:`PyFFI.Formats.CGF`
* :mod:`PyFFI.Formats.DDS`
* :mod:`PyFFI.Formats.TGA`
* :mod:`PyFFI.Formats.DAE`

If you are developing any of the above file formats, then you can specify
an alternate location where you store your own xml file by means of an
environment variable. For instance,
to tell the library to use your version of :file:`cgf.xml`,
set the :envvar:`CGFXMLPATH` environment variable to the directory where
:file:`cgf.xml` can be found. If :envvar:`CGFXMLPATH` is set, the library
will first look there. The environment variables :envvar:`NIFXMLPATH`,
:envvar:`KFMXMLPATH`, :envvar:`DDSXMLPATH`, and :envvar:`TGAXMLPATH`
work similarly.

Adding Support For New File Formats
-----------------------------------

This section tries to explain how you can implement your own format in PyFFI.

Getting Started
^^^^^^^^^^^^^^^

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
    from PyFFI.XmlFileFormat import MetaXmlFileFormat
    from PyFFI.XmlFileFormat import XmlFileFormat
    from PyFFI.ObjectModels import Common

    class SimpleFormat(XmlFileFormat):
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
  - Finally, the PyFFI.ObjectModels.Common module implements the most common basic types,
    such as integers, characters, and floats. In the above example we have
    taken advantage of Common.Int, which defines a signed 32-bit integer,
    exactly the type we need.

Reading and Writing Files
^^^^^^^^^^^^^^^^^^^^^^^^^

To read the contents of a file of the format described by
simple.xml::

    >>> from simple import SimpleFormat   #doctest: +SKIP
    >>> x = SimpleFormat.Example()        #doctest: +SKIP
    >>> f = open('somefile.simple', 'rb') #doctest: +SKIP
    >>> x.read(f)                         #doctest: +SKIP
    >>> f.close()                         #doctest: +SKIP
    >>> print(x)                          #doctest: +SKIP

Or, to create a new file in this format::

    >>> from simple import SimpleFormat   #doctest: +SKIP
    >>> x = SimpleFormat.Example()        #doctest: +SKIP
    >>> x.numIntegers = 5                 #doctest: +SKIP
    >>> x.integers.updateSize()           #doctest: +SKIP
    >>> x.integers[0] = 3                 #doctest: +SKIP
    >>> x.integers[1] = 1                 #doctest: +SKIP
    >>> x.integers[2] = 4                 #doctest: +SKIP
    >>> x.integers[3] = 1                 #doctest: +SKIP
    >>> x.integers[4] = 5                 #doctest: +SKIP
    >>> f = open('pi.simple', 'wb')       #doctest: +SKIP
    >>> x.write(f)                        #doctest: +SKIP
    >>> f.close()                         #doctest: +SKIP

Further References
^^^^^^^^^^^^^^^^^^

With the above simple example in mind, you may wish to browse through the
source code of
:mod:`PyFFI.Formats.CGF` or :mod:`PyFFI.Formats.NIF` to see how PyFFI works for more
complex file formats.
"""
__docformat__ = "restructuredtext en" # for epydoc

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

__version__ = '1.2.4'

__hexversion__ = eval('0x%02X%02X%02X'
                      % tuple(int(x) for x in __version__.split('.')))

