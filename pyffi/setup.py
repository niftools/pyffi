"""A Python library for processing block structured binary files.

The Python File Format Interface aims to make it easy to manipulate
binary files in a Python environment. Starting from a file format
description written in XML, PyFFI creates customizable Python classes
to read and write file blocks as described by the XML. Currently,
PyFFI supports the NetImmerse/Gamebryo NIF and KFM formats,
CryTek's CGF format, the DDS format, and the TGA format. Many tools
for files used by 3D games, such as a stripifier, and a tangent space
calculator, are included in PyFFI as well.

QSkope is PyFFI's graphical user interface, and enables simple editing
of files in any fileformat supported by PyFFI. QSkope depends on PyQt4,
which you can download from

http://www.riverbankcomputing.co.uk/software/pyqt/download"""

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
    packages = ['PyFFI', 'PyFFI.ObjectModels', 'PyFFI.ObjectModels.XML', 'PyFFI.ObjectModels.XSD', 'PyFFI.Utils', 'PyFFI.Formats', 'PyFFI.Formats.NIF', 'PyFFI.Formats.KFM', 'PyFFI.Formats.CGF', 'PyFFI.Formats.DDS', 'PyFFI.Formats.TGA', 'PyFFI.Spells', 'PyFFI.Spells.CGF', 'PyFFI.Spells.NIF', 'PyFFI.Spells.KFM', 'PyFFI.QSkope', 'PyFFI.Formats.DAE'],
    package_data = {'': ['*.xml', '*.xsd']}, # include xml and xsd files
    scripts = ['scripts/NIF/ffvt3rskinpartition.py', 'scripts/NIF/nifmakehsl.py', 'scripts/NIF/niftoaster.py', 'scripts/NIF/nifoptimize.py', 'scripts/NIF/niftexdump.py', 'scripts/NIF/nifdump.py', 'scripts/CGF/cgftoaster.py', 'scripts/KFM/kfmtoaster.py', 'scripts/qskope.py', 'scripts/CGF/crydaefilter.py'],
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

