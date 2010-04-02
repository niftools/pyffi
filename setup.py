"""Setup script for PyFFI."""

classifiers = """\
Development Status :: 4 - Beta
License :: OSI Approved :: BSD License
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Topic :: Multimedia :: Graphics :: 3D Modeling
Programming Language :: Python
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.0
Programming Language :: Python :: 3.1
Programming Language :: Python :: 3.2
Operating System :: OS Independent"""
#Topic :: Formats and Protocols :: Data Formats

from distutils.core import setup
import sys

if sys.version_info < (2, 5):
    raise RuntimeError("PyFFI requires Python 2.5 or higher.")

import pyffi

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = open("README.TXT").read()

setup(
    name = "PyFFI",
    version = pyffi.__version__,
    packages = [
        'pyffi',
        'pyffi.object_models',
        'pyffi.object_models.xml',
        'pyffi.object_models.xsd',
        'pyffi.utils',
        'pyffi.formats',
        'pyffi.formats.nif',
        'pyffi.formats.kfm',
        'pyffi.formats.cgf',
        'pyffi.formats.dds',
        'pyffi.formats.tga',
        'pyffi.formats.egm',
        'pyffi.formats.egt',
        'pyffi.formats.esp',
        'pyffi.formats.tri',
        'pyffi.formats.bsa',
        'pyffi.spells',
        'pyffi.spells.cgf',
        'pyffi.spells.nif',
        'pyffi.qskope',
        'pyffi.formats.dae'],
    # include xml, xsd, dll, and exe files
    package_data = {'': ['*.xml', '*.xsd', '*.dll', '*.exe'],
                    'pyffi.formats.nif': ['nifxml/nif.xml'],
                    'pyffi.formats.kfm': ['kfmxml/kfm.xml']},
    scripts = ['scripts/nif/nifmakehsl.py', 'scripts/nif/niftoaster.py', 'scripts/cgf/cgftoaster.py', 'scripts/kfm/kfmtoaster.py', 'scripts/qskope.py'],
    author = "Amorilia",
    author_email = "amorilia@users.sourceforge.net",
    license = "BSD",
    keywords = "fileformat nif cgf binary interface stripify",
    platforms = ["any"],
    description = "Processing block structured binary files.",
    classifiers = [_f for _f in classifiers.split("\n") if _f],
    long_description = long_description,
    url = "http://pyffi.sourceforge.net/",
    download_url = "http://sourceforge.net/projects/pyffi/files/"
)
