* refactoring plans
  - common base classes for PyFFI.ObjectModels.XML.BasicBase/StructBase and
    PyFFI.ObjectModels.XSD.SimpleType/ComplexType
    (e.g. PyFFI.ObjectModel.SimpleType/ComplexType)
  - derive ObjectModels.ArrayType and ObjectModels.StructType from
    common subclass PyFFI.ObjectModels.ComplexType, use these then as base
    classes for ObjectModels.XML.Array and ObjectModels.XML.StructBase
  - use PyFFI.ObjectModels.Graph for all ObjectModels.XXX implementations
  - upgrade QSkope and XML model to use GlobalNode instead of the
    current ad hoc system with Refs
  - improve the abstract ObjectModels.Delegate classes (i.e. naming,
    true abstract base classes, defining a common interface); also perhaps
    think about deriving these delegate classes from TreeLeaf (only leafs have
    editors!)?
  - ditch version and user_version from the ObjectModels interface, and
    instead use ObjectModels.Data as a global root element that contains all
    file information with a minimal format independent interface;
    implementation plan (this is already partially implemented, namely in the
    nif format):
    + use abstract Data and Tree base classes fo the XSD parser, in
      subsequent 2.x.x releases
    + update the XML parser to follow the same scheme, when switching from
      2.x.x to 3.0.0, and document the 2.x.x -> 3.0.0 migration strategy
    + deprecate the old methods (XxxFormat.read, XxxFormat.write,
      XxxFormat.getVersion, and so on) in 3.x.x
    + remove old method in 4.x.x
  - one of the aims is that qskope no longer relies on any
    ObjectModels.XML/ObjectModels.XSD specific implementations; if it only
    relies on the abstract base classes in ObjectModels.Graph and
    ObjectModels.Data then future expansions are a lot easier to cope with;
    in particular, qskope should never have to import from ObjectModels.XXX,
    or Formats.XXX

* use logging module for all log actions

* doctests for all spells

* improve overall documentation, for instance:
  - add docstrings for all spells
  - add docstrings for all spell methods

* move all regression tests to the tests directory (but keep useful examples
  in the docstrings!)

* add spell support for qskope directly using the PyFFI.Spells module

* allow qskope to create new spells, from a user supplied spells module
  - custom spell module creation wizard (creates dir structure for user
    and stores it into the configuration)
  - custom spell creation wizard (adds new spell to user's spell module)
  - automatic templates for typical spells

* pep8 conventions
  - resolve all complaints from cheesecake's pep8 checker

* use partial metaclass for all customizers

Unsure things
-------------

* pep8 case conventions
  these would obviously break backwards compatibility, not sure how to deal
  with it... probably this will never be done, gains are minimal and effort
  is huge:
  - lower case for all modules
  - lower case for all methods and attributes

