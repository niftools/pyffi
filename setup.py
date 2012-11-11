"""Setup script for PyFFI."""

classifiers = """\
Development Status :: 4 - Beta
License :: OSI Approved :: BSD License
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Topic :: Multimedia :: Graphics :: 3D Modeling
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.0
Programming Language :: Python :: 3.1
Programming Language :: Python :: 3.2
Operating System :: OS Independent"""
#Topic :: Formats and Protocols :: Data Formats

from distutils.core import setup
import sys

if sys.version_info < (3, 0):
    raise RuntimeError("PyFFI requires Python 3.0 or higher.")

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = open("README.TXT").read()

with open("pyffi/VERSION", "rt") as f:
    version = f.read().strip()

setup(
    name = "PyFFI",
    version = version,
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
        'pyffi.formats.psk',
        'pyffi.formats.rockstar',
        'pyffi.formats.rockstar.dir_',
        'pyffi.spells',
        'pyffi.spells.cgf',
        'pyffi.spells.nif',
        'pyffi.qskope',
        'pyffi.formats.dae'],
    # include xml, xsd, dll, and exe files
    package_data = {'': ['*.xml', '*.xsd', '*.dll', '*.exe'],
                    'pyffi.formats.nif': ['nifxml/nif.xml'],
                    'pyffi.formats.kfm': ['kfmxml/kfm.xml'],
                    'pyffi': ['VERSION'],
                   },
    scripts = [
        'scripts/nif/nifmakehsl.py',
        'scripts/nif/niftoaster.py',
        'scripts/cgf/cgftoaster.py',
        'scripts/kfm/kfmtoaster.py',
        'scripts/rockstar_pack_dir_img.py',
        'scripts/rockstar_unpack_dir_img.py',
        'scripts/patch_recursive_make.py',
        'scripts/patch_recursive_apply.py',
        'scripts/qskope.py'],
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
