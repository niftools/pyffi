"""Setup script for PyFFI."""

classifiers = """\
Development Status :: 4 - Beta
License :: OSI Approved :: BSD License
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Topic :: Multimedia :: Graphics :: 3D Modeling
Programming Language :: Python
Operating System :: OS Independent"""
#Topic :: Formats and Protocols :: Data Formats

from distutils.core import setup
import sys

if sys.version_info < (2, 5):
    raise RuntimeError("PyFFI requires Python 2.5 or higher.")

import PyFFI

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = open("README.TXT").read()

setup(
    name = "PyFFI",
    version = PyFFI.__version__,
    packages = ['PyFFI', 'PyFFI.object_models', 'PyFFI.object_models.xml', 'PyFFI.object_models.xsd', 'PyFFI.utils', 'PyFFI.Formats', 'PyFFI.Formats.NIF', 'PyFFI.Formats.KFM', 'PyFFI.Formats.CGF', 'PyFFI.Formats.DDS', 'PyFFI.Formats.TGA', 'PyFFI.spells', 'PyFFI.spells.cgf', 'PyFFI.spells.nif', 'PyFFI.qskope', 'PyFFI.Formats.DAE'],
    package_data = {'': ['*.xml', '*.xsd', '*.dll', '*.exe']}, # include xml, xsd, dll, and exe files
    scripts = ['scripts/nif/nifmakehsl.py', 'scripts/nif/niftoaster.py', 'scripts/cgf/cgftoaster.py', 'scripts/kfm/kfmtoaster.py', 'scripts/qskope.py'],
    author = "Amorilia",
    author_email = "amorilia@users.sourceforge.net",
    license = "BSD",
    keywords = "fileformat nif cgf binary interface stripify",
    platforms = ["any"],
    description = "Processing block structured binary files.",
    classifiers = filter(None, classifiers.split("\n")),
    long_description = long_description,
    url = "http://pyffi.sourceforge.net/",
    download_url = "http://sourceforge.net/project/showfiles.php?group_id=199269"
)
