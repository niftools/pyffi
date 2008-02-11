"""A Python library for reading, writing, and processing binary files.

The Python File Format Interface aims to make it easy to manipulate
binary files in a Python environment. Starting from a file format
description written in XML, PyFFI creates customizable Python classes
to read and write file blocks as described by the XML. Currently,
PyFFI supports the NetImmerse/Gamebryo NIF format, and CryTek's CGF
format. Many tools for files used by 3D games, such as a stripifier,
and a tangent space calculator, are included in PyFFI as well.

QSkope is PyFFI's graphical user interface, and enables simple editing of
files in any fileformat supported by PyFFI. QSkope depends on PyQt4, which you
can download from

http://www.riverbankcomputing.co.uk/pyqt/download.php"""

classifiers = """\
Development Status :: 4 - Beta
License :: OSI Approved :: BSD License
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Topic :: Multimedia :: Graphics :: 3D Modeling
Programming Language :: Python
Operating System :: OS Independent"""
#Topic :: Formats and Protocols :: Data Formats

doclines = __doc__.split("\n")

from distutils.core import setup
import sys

if sys.version_info < (2, 5):
    raise RuntimeError("PyFFI requires Python 2.5 or higher.")

import PyFFI

setup(
    name = "PyFFI",
    version = PyFFI.__version__,
    packages = ['PyFFI', 'PyFFI.Bases', 'PyFFI.Utils', 'PyFFI.NIF', 'PyFFI.KFM', 'PyFFI.CGF', 'NifTester', 'NifTester.hacking', 'NifTester.validate', 'NifTester.surgery', 'NifVis', 'NifVis.lizers', 'CgfTester', 'CgfTester.hacking', 'CgfTester.validate', 'CgfTester.surgery', 'KfmTester', 'KfmTester.hacking', 'KfmTester.validate', 'KfmTester.surgery', 'qskopelib'],
    package_dir = { 'NifTester' : 'tools/NIF/NifTester', 'NifVis' : 'tools/NIF/NifVis', 'CgfTester' : 'tools/CGF/CgfTester', 'KfmTester' : 'tools/KFM/KfmTester', 'qskopelib' : 'tools/qskopelib' },
    package_data = { '' : [ '*.xml' ] }, # include xml files
    scripts = ['pyffipostinstallation.py', 'tools/NIF/ffvt3rskinpartition.py', 'tools/NIF/nifmakehsl.py', 'tools/NIF/niftoaster.py', 'tools/NIF/nifvisualizer.py', 'tools/NIF/nifoptimize.py', 'tools/NIF/niftexdump.py', 'tools/NIF/nifdump.py', 'tools/NIF/niftemplate.py', 'tools/CGF/cgftoaster.py', 'tools/KFM/kfmtoaster.py', 'tools/qskope.py'],
    author = "Amorilia",
    author_email = "amorilia@users.sourceforge.net",
    license = "BSD",
    keywords = "fileformat nif cgf binary interface stripify", 
    platforms = ["any"],
    description = doclines[0],
    classifiers = filter(None, classifiers.split("\n")),
    long_description = "\n".join(doclines[2:]),
    url = "http://pyffi.sourceforge.net/",
    download_url = "http://sourceforge.net/project/showfiles.php?group_id=199269"
)

