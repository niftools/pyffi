The Python File Format Interface, briefly PyFFI, is an open source
Python library for processing block structured binary files:

* **Simple:** Easy to read, write, and manipulate complex binary files
  in a Python environment. Currently, PyFFI supports the
  NetImmerse/Gamebryo NIF and KFM formats, CryTek's CGF format, the
  DDS format, and the TGA format.

* **Batteries included:** Many tools for files used by 3D games, such
  as a stripifier, tangent space calculator, 2d/3d hull algorithms,
  inertia calculator, as well as a general purpose file editor
  :program:`QSkope` (using `PyQt4
  <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_), are
  all included.

* **Modular:** Its highly modular design make it easy to add support
  for new formats, and also to extend existing functionality.

Download
--------

Get PyFFI from
`Sourceforge <http://sourceforge.net/project/showfiles.php?group_id=199269>`_,
or install it with::

    easy_install -U PyFFI

To get the latest (but possibly unstable) code, clone PyFFI from its
`Git repository <http://github.com/amorilia/pyffi>`_. If you wish to
code on PyFFI and send your contributions back upstream, get a `github
account <https://github.com/signup/free>`_ and `fork PyFFI
<http://github.com/guides/fork-a-project-and-submit-your-modifications>`_.

Examples
--------

* The `Blender NIF Scripts
  <http://sourceforge.net/project/showfiles.php?group_id=149157&package_id=166219>`_
  and the `Blender CGF Scripts
  <http://sourceforge.net/project/showfiles.php?group_id=235915>`_ use
  PyFFI to import and export these files to and from Blender.

* :program:`QSkope`, PyFFI's general purpose file editor.

* The :program:`niftoaster` spells use PyFFI for instance for
  `optimizing nif files
  <http://cs.elderscrolls.com/constwiki/index.php/Nif_Optimization>`_,
  and much more.

Questions? Suggestions?
-----------------------

* Open an issue at the `tracker
  <http://sourceforge.net/tracker/?group_id=199269>`_.

* You can also come to the ``#niftools`` channel on FreeNode.

..
  See http://pyffi.sourceforge.net/ for more information and documentation.
