PyFFI
=====
.. image:: https://img.shields.io/travis/niftools/pyffi/develop.svg?label=Linux%20Build&logo=travis
    :target: https://travis-ci.org/niftools/pyffi

.. image:: https://img.shields.io/appveyor/ci/neomonkeus/pyffi/develop.svg?label=Windows%20Build&logo=appveyor
    :target: https://ci.appveyor.com/project/neomonkeus/pyffi

.. image:: https://img.shields.io/coveralls/github/niftools/pyffi/develop.svg?label=Coverage
    :target: https://coveralls.io/r/niftools/pyffi?branch=develop

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
Get PyFFI from `Github <https://github.com/niftools/pyffi/releases>`_,
or install it with::

    easy_install -U PyFFI

or::

    pip3 install PyFFI

Developing
----------
To get the latest (but possibly unstable) code, clone PyFFI from its
`Git repository <http://github.com/niftools/pyffi>`_::

    git clone --recursive git://github.com/niftools/pyffi.git
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

Be sure to use the --recursive flag to ensure that you also get all
of the submodules.

If you wish to code on PyFFI and send your contributions back upstream,
get a `github account <https://github.com/signup/free>`_ and `fork PyFFI
<http://help.github.com/fork-a-repo/>`_.

Testing
-------
We love tests, they help guarantee that things keep working they way
they should. You can run them yourself with the following::

    source venv/bin/activate
    nosetest -v test

or::

    source venv/bin/activate
    py.test -v tests

Documentation
-------------
All our documentation is written in ReST and can be generated into HTML,
LaTeX, PDF and more thanks to Sphinx. You can generate it yourself::

    source venv/bin/activate
    cd docs
    make html -a

Examples
--------
* The `Blender NIF Plugin
  <https://github.com/niftools/blender_nif_plugin>`_

* QSkope PyFFI's general purpose file editor.

* The niftoaster (PyFFI's "swiss army knife") can for instance
  `optimize NIF files
  <http://cs.elderscrolls.com/index.php?title=Nif_Optimization>`_,
  and much more.

Questions? Suggestions?
-----------------------
* Open an issue at the `issue tracker
  <https://github.com/niftools/pyffi/issues>`_.

..
  See http://www.niftools.org/ for more information and documentation.
