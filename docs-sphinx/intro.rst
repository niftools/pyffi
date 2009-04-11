Introduction
============

Example and Problem Description
-------------------------------

Consider an application which processes images stored in for instance
the Targa format::

    >>> # read the file
    >>> stream = open("test/tga/test.tga", "rb")
    >>> data = stream.read()
    >>> # do something with the data...
    >>> data[8] = 20 # change x origin
    >>> data[10] = 20 # change y origin
    >>> # etc... until we are finished processing the data
    >>> # write the file
    >>> stream = open("modified.tga", "wb")
    >>> stream.write(data)

This methodology will work for any file format, but it is usually not
very convenient. For complex file formats, the *do something with the
data* part of the program would be necessarily quite complicated for
the programmer. For this reason, it is convenient to convert the data
(a sequence of bytes) into an organized collection of Python objects
(a class suits this purpose perfectly) that clearly reveal what is
stored in the data. Such organized collection is called an
:term:`interface`::

    >>> import struct
    >>> class TgaFile:
    ...     """A simple class for reading and writing Targa files."""
    ...     def read(self, filename):
    ...         """Read tga file from stream."""
    ...         stream = open(filename, "rb")
    ...         self.image_id_length, self.colormap_type, self.image_type, \
    ...         self.colormap_index, self.colormap_length, self.colormap_size, \
    ...         self.x_origin, self.y_origin, self.width, self.height, \
    ...         self.pixel_size, self.flags = struct.unpack("<BBBHHBHHHHBB",
    ...                                                     stream.read(18))
    ...         self.image_id = stream.read(id_length)
    ...         if self.colormap_type:
    ...             self.colormap = [
    ...                 stream.read(self.colormap_size >> 3)
    ...                 for i in range(self.colormap_length)]
    ...         self.image = [[stream.read(self.pixel_size >> 3)
    ...                        for i in xrange(self.width)]
    ...                       for j in xrange(self.height)]
    ...         stream.close()
    ...     def write(self, filename):
    ...         """Read tga file from stream."""
    ...         stream = open(filename, "wb")
    ...         stream.write(struct.pack("<BBBHHBHHHHBB",
    ...             self.image_id_length, self.colormap_type, self.image_type,
    ...             self.colormap_index, self.colormap_length,
    ...             self.colormap_size,
    ...             self.x_origin, self.y_origin, self.width, self.height,
    ...             self.pixel_size, self.flags))
    ...         stream.write(self.image_id)
    ...         for entry in self.colormap:
    ...             stream.write(entry)
    ...         for line in self.image:
    ...             for pixel in line:
    ...                 stream.write(pixel)
    >>> data = TgaFile()
    >>> # read the file
    >>> data.read("test/tga/test.tga")
    >>> # do something with the data...
    >>> data.x_origin = 20
    >>> data.y_origin = 20
    >>> # etc... until we are finished processing the data
    >>> # write the file
    >>> data.write("modified.tga")

The reading and writing part of the code has become a lot more
complicated, but the benefit is immediately clear: instead of working
with a sequence of bytes, we can directly work with the members of our
``TgaFile`` class, and our code no longer depends on how exactly image
data is organized in a Targa file. In other words, the *do something
with the data* part of our code can now use the semantics of the
``TgaFile`` class, and is consequently much easier to understand and
to maintain.

In practice, however, when taking the above approach as given, the
additional code that enables this semantic translation is often
difficult to maintain, for the following reasons:

* **Duplication:** Any change in the reader part must be reflected in
  the writer part, and vice versa. Moreover, the same data types tend
  to occur again and again, leading to nearly identical code for each
  read/write operation. A partial solution to this problem would be to
  create an additional class for each data type, each with its read
  and write method.

* **No validation:** What if :file:`test/tga/test.tga` is not a Targa
  file at all, or is corrupted? What if ``image_id`` changes length
  but ``image_id_length`` is not updated accordingly? Can we catch
  such bugs and prevent data to become corrupted?

* **Boring:** Writing :term:`interface` code gets boring very quickly.

What is PyFFI?
--------------

PyFFI aims to solve all of the above problems:

* The classes for an :term:`interface` are *generated at runtime*,
  from an easy to maintain description of the file format. In this
  way, PyFFI provides access to *all* information that comes naturally
  from files.

* Validation is automatically enforced by the generated classes,
  except in a few rare cases when automatic validation might induce
  substantial overhead. These cases are well documented and simply
  require the user to call the validation method explicitly.

* The generated interfaces can easily be extended with additional
  class methods, for instance to provide common calculations (for
  example: converting a single pixel into greyscale).

* Very high level functions can be implemented as a :term:`spell` (for
  example: convert a height map into a normal map).

**FOLLOWING NEEDS TO MOVE**
If you are developing a particular file format, then you can specify
an alternate location of your xml file, for instance :file:`cgf.xml`,
by setting the :envvar:`CGFXMLPATH` environment variable to the directory where
:file:`cgf.xml` can be found. If :envvar:`CGFXMLPATH` is set, the library will first
look there. The same applies to all other formats.

**FOLLOWING NEEDS TO BE REWRITTEN**
The code is organized as follows.

* Python File Format Interface - representing a file format specified by an XML
  file in Python

  - PyFFI/__init__.py

    Contains the main metaclass which generates classes for each type
    defined in the XML.

  - PyFFI/XmlHandler.py

    The XML handler, contains the core code that transforms the XML
    file into classes. The parser code is based on NifSkope's XML
    parser (see http://niftools.sourceforge.net).

  - PyFFI/ObjectModels/

    All base classes for various classes generated by the
    XmlFileFormat metaclass, i.e. basic and struct. Also contains
    the implementation of array's and the expression parser.

* CGF Format Library - instantiates classes, and customize them

  - PyFFI/Formats/CGF/__init__.py: instantiates classes for the CGF format

  - PyFFI/Formats/CGF/\*.py: customization of particular blocks

* NIF, KFM, TGA, and DDS Format Library - similar to CGF

* Utilities

  - PyFFI/Utils/__init__.py: collection of random small utilities

    + hexDump: dump file chunk in hexadecimal format

    + walk: a variant of os.walk()

    + TriStrip: stripifier utilities (uses a Python port of NvTriStrip)

    + MathUtils: common vector and matrix operations

    + QuickHull: a simple implementation of the 2d and 3d quick hull
      algorithms

    + Inertia: a library for calculating mass, center of gravity, and inertia
      tensor of common shapes

  - PyFFI/Spells/NIF and PyFFI/Spells/CGF: format specific helper modules

  - PyFFI/QSkope: modules used by QSkope (PyFFI's GUI application)

  - scripts/NIF, scripts/CGF, ...: format specific scripts

    + niftoaster, cgftoaster, ...: for hacking files with spells

    + ffvt3rskinpartition: skin partition calculator for Freedom Force vs. The
      3rd Reich

    + nifmakehsl: create hex workshop structure libraries for all nif formats

    + nifoptimize: remove redundant vertices and restripify nif files

* Documentation - generated by epydoc

  - docs/...

* Test files

  - tests/...

* examples

  - examples/simple

    Simple example on how to implement a new format.

  - examples/metaclasses/howto_generate_class_from_xml.py

    Proof of concept of how classes can be generated from an xml
    description. I keep it there as it could be useful to get a quick
    idea of how the XML is converted to a bunch of classes.

The following code resides in the git repository only
(http://github.com/amorilia/pyffi) and is not distributed
with the library.

* various scripts

  - rundoctest.py: runs all tests in the documentation

  - makezip.sh: script which creates the distribution packages

  - pylintrc: pylint configuration file

