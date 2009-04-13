"""
.. :mod:`PyFFI.Formats` --- File format interfaces
   ===============================================

When experimenting with any of the supported file formats, you can specify
an alternate location where you store your modified format description by means
of an environment variable. For instance,
to tell the library to use your version of :file:`cgf.xml`,
set the :envvar:`CGFXMLPATH` environment variable to the directory where
:file:`cgf.xml` can be found. The environment variables :envvar:`NIFXMLPATH`,
:envvar:`KFMXMLPATH`, :envvar:`DDSXMLPATH`, and :envvar:`TGAXMLPATH`
work similarly.

Supported formats
-----------------

.. toctree::
   :maxdepth: 2
   
   PyFFI.Formats.CGF
   PyFFI.Formats.DAE
   PyFFI.Formats.DDS
   PyFFI.Formats.KFM
   PyFFI.Formats.NIF
   PyFFI.Formats.TGA

Adding new formats
------------------

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
