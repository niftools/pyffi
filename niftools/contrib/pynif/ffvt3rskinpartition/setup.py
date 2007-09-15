"""Update skin partitions for Freedom Force vs. the 3rd Reich.

This script updates skin partitions of all nif files in a given directory tree.
The nif files are modified, in particular if something goes wrong this script
may destroy your files. Make a backup before running this script."""

classifiers = """\
Development Status :: 4 - Beta
License :: OSI Approved :: BSD License
Intended Audience :: End Users/Desktop
Topic :: Multimedia :: Graphics :: 3D Modeling
Programming Language :: Python
Operating System :: OS Independent
"""

doclines = __doc__.split("\n")

from distutils.core import setup
import sys

if sys.version_info < (2, 5):
    raise RuntimeError("Requires Python 2.5 or higher.")

setup(
    name = "ffvt3rskinpartition",
    version = "1.0",
    scripts = ['ffvt3rskinpartition.py'],
    author = "Amorilia",
    author_email = "amorilia@gamebox.net",
    license = "BSD",
    keywords = "nif skin partition freedom force", 
    platforms = ["any"],
    description = doclines[0],
    classifiers = filter(None, classifiers.split("\n")),
    long_description = "\n".join(doclines[2:]),
    url = "http://niftools.sourceforge.net/",
#    download_url = "http://sourceforge.net/project/showfiles.php?..."
)

