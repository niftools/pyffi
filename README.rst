The Python File Format Interface, briefly PyFFI, is an open source
Python library for processing block structured binary files:

* **Simple:** Reading, writing, and manipulating complex binary files
  in a Python environment is easy! Currently, PyFFI supports the
  NetImmerse/Gamebryo NIF and KFM formats, CryTek's CGF format, the
  FaceGen EGM format, the DDS format, and the TGA format.

* **Batteries included:** Many tools for files used by 3D games, such
  as optimizers, stripifier, tangent space calculator, 2d/3d hull
  algorithms, inertia calculator, as well as a general purpose file
  editor QSkope (using `PyQt4
  <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_), are
  included.

* **Modular:** Its highly modular design makes it easy to add support
  for new formats, and also to extend existing functionality.

Download
--------

Get PyFFI from
`Github <https://github.com/niftools/pyffi/releases>`_,
or install it with::

    easy_install -U PyFFI

or::
    pip3 install PyFFI

To get the latest (but possibly unstable) code, clone PyFFI from its
`Git repository <http://github.com/niftools/pyffi>`_::

    git clone --recursive git://github.com/niftools/pyffi.git

Be sure to use the --recursive flag to ensure that you also get all
of the submodules.

If you wish to
code on PyFFI and send your contributions back upstream, get a `github
account <https://github.com/signup/free>`_ and `fork PyFFI
<http://help.github.com/fork-a-repo/>`_.

Examples
--------

* The `Blender NIF Plugin
  <https://github.com/niftools/blender_nif_plugin>`_

* QSkope PyFFI's general purpose file editor.

* The niftoaster (PyFFI's "swiss army knife") can for instance
  `optimize nif files
  <http://cs.elderscrolls.com/index.php?title=Nif_Optimization>`_,
  and much more.

Questions? Suggestions?
-----------------------

* Open an issue at the `issue tracker
  <https://github.com/niftools/pyffi/issues>`_.

..
  See http://www.niftools.org/ for more information and documentation.
