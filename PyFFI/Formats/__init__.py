"""
:mod:`PyFFI.Formats` --- File format interfaces
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
by creating an XML file, call it :file:`simple.xml`, which describes this format
in a way that PyFFI can understand:

.. literalinclude:: ../examples/simple/simple.xml
    :language: xml

What PyFFI does is convert this simple XML description into Python classes
which automatically can read and write the structure you've just described.
Say this is the contents of :file:`simple.py`:

.. literalinclude:: ../examples/simple/simple.py
    :language: python

What happens in this piece of code?

  - The :class:`PyFFI.ObjectModels.XML.FileFormat.XmlFileFormat`
    base class triggers the transformation of xml into Python classes;
    how these classes can be used will be explained further.

  - The :attr:`~PyFFI.ObjectModels.XML.FileFormat.XmlFileFormat.xmlFileName`
    class attribute provides the name of the xml file that describes
    the structures we wish to generate. The
    :attr:`~PyFFI.ObjectModels.XML.FileFormat.XmlFileFormat.xmlFilePath`
    attribute gives a list of locations of where to look for this
    file; in our case we have simply chosen to put :file:`simple.xml`
    in the same directory as :file:`simple.py`.

  - The :class:`SimpleFormat.Example` class
    provides the generated class with a function :meth:`addInteger` in
    addition to the attributes :attr:`numIntegers` and
    :attr:`integers` which have been created from the XML.

  - Finally, the :mod:`PyFFI.ObjectModels.Common` module implements
    the most common basic types, such as integers, characters, and
    floats. In the above example we have taken advantage of
    :class:`PyFFI.ObjectModels.Common.Int`, which defines a signed
    32-bit integer, exactly the type we need.

Reading and Writing Files
^^^^^^^^^^^^^^^^^^^^^^^^^

To read the contents of a file of the format described by
simple.xml:

.. literalinclude:: ../examples/simple/testread.py
    :language: python

Or, to create a new file in this format:

.. literalinclude:: ../examples/simple/testwrite.py
    :language: python

Further References
^^^^^^^^^^^^^^^^^^

With the above simple example in mind, you may wish to browse through
the source code of :mod:`PyFFI.Formats.CGF` or
:mod:`PyFFI.Formats.NIF` to see how PyFFI works for more complex file
formats.
"""
