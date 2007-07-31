"""A Python library for reading, writing, and processing binary files.

PyFFI reads a file format description (XML) and creates customizable
Python classes to read & write such files (e.g. Netimmerse File Format
(NIF), Crytek files (CGF)). Includes tools for files used by 3D games
(e.g. stripifier, tangent space calculation). Only the NIF format is
supported in this release."""

classifiers = """\
Development Status :: 3 - Alpha
License :: OSI-Approved Open Source :: BSD License
Intended Audience :: by End-User Class :: Developers
Intended Audience :: by End-User Class :: End Users/Desktop
Topic :: Formats and Protocols :: Data Formats
Programming Language :: Python
Operating System :: OS Independent
"""

doclines = __doc__.split("\n")

from distutils.core import setup
import sys

if sys.version_info < (2, 5):
    raise RuntimeError("PyFFI requires Python 2.5 or higher.")

setup(
    name = "PyFFI",
    version = "0.3",
    packages = ['PyFFI', 'PyFFI.Bases', 'PyFFI.Utils', 'PyFFI.NIF', 'PyFFI.CGF'],
    package_data = { '' : [ '*.xml' ] }, # include xml files
    author = "Python File Format Interface",
    author_email = "amorilia@gamebox.net",
    license = "BSD",
    keywords = "fileformat nif cgf binary interface stripify", 
    platforms = ["any"],
    description = doclines[0],
    classifiers = filter(None, classifiers.split("\n")),
    long_description = "\n".join(doclines[2:]),
    url = "http://pyffi.sourceforge.net/"
)
