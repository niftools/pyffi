Introduction
============

Example and Problem Description
-------------------------------

Consider an application which processes images stored in for instance
the Targa format::

    >>> # read the file
    >>> stream = open("tests/tga/test.tga", "rb")
    >>> data = bytearray(stream.read()) # read bytes
    >>> stream.close()
    >>> # do something with the data...
    >>> data[8] = 20 # change x origin
    >>> data[10] = 20 # change y origin
    >>> # etc... until we are finished processing the data
    >>> # write the file
    >>> from tempfile import TemporaryFile
    >>> stream = TemporaryFile()
    >>> dummy = stream.write(data) # py3k returns number of bytes written
    >>> stream.close()

This methodology will work for any file format, but it is usually not
very convenient. For complex file formats, the *do something with the
data* part of the program would be necessarily quite complicated for
the programmer. For this reason, it is convenient to convert the data
(a sequence of bytes) into an organized collection of Python objects
(a class suits this purpose perfectly) that clearly reveal what is
stored in the data. Such organized collection is called an
:term:`interface`::

    >>> import struct
    >>> from tempfile import TemporaryFile
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
    ...         self.image_id = stream.read(self.image_id_length)
    ...         if self.colormap_type:
    ...             self.colormap = [
    ...                 stream.read(self.colormap_size >> 3)
    ...                 for i in range(self.colormap_length)]
    ...         else:
    ...             self.colormap = []
    ...         self.image = [[stream.read(self.pixel_size >> 3)
    ...                        for i in range(self.width)]
    ...                       for j in range(self.height)]
    ...         stream.close()
    ...     def write(self, filename=None):
    ...         """Read tga file from stream."""
    ...         if filename:
    ...             stream = open(filename, "wb")
    ...         else:
    ...             stream = TemporaryFile()
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
    ...         stream.close()
    >>> data = TgaFile()
    >>> # read the file
    >>> data.read("tests/tga/test.tga")
    >>> # do something with the data...
    >>> data.x_origin = 20
    >>> data.y_origin = 20
    >>> # etc... until we are finished processing the data
    >>> # write the file
    >>> data.write()

The reading and writing part of the code has become a lot more
complicated, but the benefit is immediately clear: instead of working
with a sequence of bytes, we can directly work with the members of our
``TgaFile`` class, and our code no longer depends on how exactly image
data is organized in a Targa file. In other words,
our code can now use the semantics of the
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

* The :term:`interface` classes are *generated at runtime*, from an
  easy to maintain description of the file format. The generated
  classes provides semantic access to *all* information in the files.

* Validation is automatically enforced by the generated classes,
  except in a few rare cases when automatic validation might cause
  substantial overhead. These cases are well documented and simply
  require an explicit call to the validation method.

* The generated classes can easily be extended with additional class
  methods, for instance to provide common calculations (for example:
  converting a single pixel into greyscale).

* Very high level functions can be implemented as :term:`spell`\ s (for
  example: convert a height map into a normal map).

