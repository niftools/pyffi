"""
.. note::

   The documentation of this module is not yet entirely complete.

This module bundles all file format object models. An object model
is a group of classes whose instances can hold the information
contained in a file whose format is described in a particular way
(xml, xsd, and possibly others).

There is a strong distinction between types that contain very specific
simple data (SimpleType) and more complex types that contain groups of
simple data (ComplexType, with its descendants StructType for named
lists of objects of different type and ArrayType for indexed lists of
objects of the same type).

The complex types are generic in that they can be instantiated using
metadata (i.e. data describing the structure of the actual file data)
from xml, xsd, or any other file format description.

For the simple types there are specific classes implementing access to
these data types. Typical implementations are present for integers,
floats, strings, and so on. Some simple types may also be derived from
already implemented simple types, if the metadata description allows
this.
"""
