"""
:mod:`PyFFI.Formats` --- Supported file formats
===============================================

When experimenting with any of the supported file formats, you can specify
an alternate location where you store your modified format description by means
of an environment variable. For instance,
to tell the library to use your version of :file:`cgf.xml`,
set the :envvar:`CGFXMLPATH` environment variable to the directory where
:file:`cgf.xml` can be found. The environment variables :envvar:`NIFXMLPATH`,
:envvar:`KFMXMLPATH`, :envvar:`DDSXMLPATH`, and :envvar:`TGAXMLPATH`
work similarly.

.. toctree::
   :maxdepth: 2
   
   formats/cgf
   formats/dae
   formats/dds
   formats/kfm
   formats/nif
   formats/tga
"""
__docformat__ = "restructuredtext en" # for epydoc
