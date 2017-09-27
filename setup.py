import sys, os
from setuptools import setup
from sphinx.setup_command import BuildDoc

on_rtd = os.getenv('READTHEDOCS') == 'True'

requirements = []
with open('requirements-dev.txt') as f:
    requirements = f.read().splitlines()

if on_rtd:
    requirements.append('sphinxcontrib-napoleon')

cmdclass = {
    'build_docs': BuildDoc
}

"""Setup script for PyFFI."""

classifiers = """\
Development Status :: 4 - Beta
License :: OSI Approved :: BSD License
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
Topic :: Multimedia :: Graphics :: 3D Modeling
Programming Language :: Python
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Operating System :: OS Independent"""
# Topic :: Formats and Protocols :: Data Formats

if sys.version_info < (3, 3):
    raise RuntimeError("PyFFI requires Python 3.3 or higher.")

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = open("README.TXT").read()

with open("pyffi/VERSION", "rt") as f:
    version = f.read().strip()

setup(
    name="PyFFI",
    version=version,
    packages=[
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
    package_data={'': ['*.xml', '*.xsd', '*.dll', '*.exe'],
                  'pyffi.formats.nif': ['nifxml/nif.xml'],
                  'pyffi.formats.kfm': ['kfmxml/kfm.xml'],
                  'pyffi': ['VERSION'],
                  },
    scripts=[
        'scripts/nif/nifmakehsl.py',
        'scripts/nif/niftoaster.py',
        'scripts/cgf/cgftoaster.py',
        'scripts/kfm/kfmtoaster.py',
        'scripts/rockstar_pack_dir_img.py',
        'scripts/rockstar_unpack_dir_img.py',
        'scripts/patch_recursive_make.py',
        'scripts/patch_recursive_apply.py',
        'scripts/qskope.py'],
    author="Niftools Developers",
    cmdclass=cmdclass,
    # these are optional and override conf.py settings
    command_options={
        'build_docs': {
            'project': ('setup.py', "PyFFI"),
            'version': ('setup.py', version),
            'release': ('setup.py', version),
            'source_dir': ('setup.py', 'docs/')
        }
    },
    license="BSD",
    keywords="fileformat nif cgf binary interface stripify",
    platforms=["any"],
    description="Processing block structured binary files.",
    classifiers=[_f for _f in classifiers.split("\n") if _f],
    long_description=long_description,
    url="https://github.com/niftools/pyffi",
    download_url="https://github.com/niftools/pyffi/releases",
    install_requires=requirements
)
