PyFFI can be installed in three ways:
- download and run the Windows installer
- install manually using setuptools (easy_install)
- install manually from the source package

Requirements
============

To run PyFFI's graphical file editor QSkope, you need PyQt4, which you
can download from

http://www.riverbankcomputing.co.uk/software/pyqt/download

Manual installation
===================

Uninstall
---------

If you install PyFFI manually, and you already have an older version
of PyFFI installed, then first uninstall this old version before
installing the new one.  You can uninstall PyFFI manually simply by
deleting the PyFFI folder from your Python's site-packages folder,
which is typically at

C:\Python25\Lib\site-packages\PyFFI

or

/usr/lib/python2.5/site-packages/PyFFI

Note that the Windows installer will perform this step automatically for you.

Via setuptools
--------------

If you have setuptools installed
(http://peak.telecommunity.com/DevCenter/setuptools), simply run

  easy_install PyFFI

at the command prompt.

From source package
-------------------

Untar or unzip the source via either

  tar xfvz PyFFI-x.x.x.tar.gz

or

  unzip PyFFI-x.x.x.zip 

Change to the PyFFI directory

  cd PyFFI-x.x.x

Finally, run the setup script,

  python setup.py install

