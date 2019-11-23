"""Setup script for PyFFI."""

import os
import sys

if sys.version_info < (3, 3):
    raise RuntimeError("PyFFI requires Python 3.3 or higher.")

NAME = "PyFFI"
with open("pyffi/VERSION", "rt") as f:
    VERSION = f.read().strip()
PACKAGES = [
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
    'pyffi.formats.dae']

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Topic :: Multimedia :: Graphics :: 3D Modeling',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Operating System :: OS Independent']

try:
    LONG_DESCRIPTION = open("README.rst").read()
except IOError:
    LONG_DESCRIPTION = open("README.TXT").read()

# include xml, xsd, dll, and exe files
PACKAGE_DATA = {'': ['*.xml', '*.xsd', '*.dll', '*.exe'],
                'pyffi.formats.nif': ['nifxml/nif.xml'],
                'pyffi.formats.kfm': ['kfmxml/kfm.xml'],
                'pyffi': ['VERSION'],
                }
SCRIPTS = ['scripts/nif/nifmakehsl.py',
           'scripts/nif/niftoaster.py',
           'scripts/cgf/cgftoaster.py',
           'scripts/kfm/kfmtoaster.py',
           'scripts/rockstar_pack_dir_img.py',
           'scripts/rockstar_unpack_dir_img.py',
           'scripts/patch_recursive_make.py',
           'scripts/patch_recursive_apply.py',
           'scripts/qskope.py']
AUTHOR = "Niftools Developers"
AUTHOR_EMAIL = "info@niftools.org"
LICENSE = "BSD"
KEYWORDS = "fileformat nif cgf binary interface stripify"
PLATFORMS = ["any"]
DESCRIPTION = "Processing block structured binary files."
URL = "https://github.com/niftools/pyffi"
DOWNLOAD_URL = "https://github.com/niftools/pyffi/releases"

try:
    from sphinx.setup_command import BuildDoc
except ImportError:
    from pyffi.utils import BuildDoc

CMD_CLASS = {'build_docs': BuildDoc}
COMMAND_OPTIONS = {
    'build_docs': {
        'project': ('setup.py', "PyFFI"),
        'version': ('setup.py', VERSION),
        'release': ('setup.py', VERSION),
        'source_dir': ('setup.py', 'docs/')
    }
}

params = dict(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    scripts=SCRIPTS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    cmdclass=CMD_CLASS,
    command_options=COMMAND_OPTIONS,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    extras_require={}
)

REQ_DIR = os.path.join(os.path.dirname(__file__), "requirements")


def parse_requirements(requirement_file):
    requirements = []
    req_path = os.path.join(REQ_DIR, requirement_file)
    with open(req_path) as file_pointer:
        for line in file_pointer:
            if line.strip() and not line.strip().startswith('#'):
                requirements.append(line.strip())
    return requirements


def add_per_version_requirements():
    extra_requires_dict = {}
    for current_file in os.listdir(REQ_DIR or '.'):  # the '.' allows tox to be run locally
        if not current_file.startswith('requirements-') or 'docs' in current_file and 'dev' not in current_file:
            continue
        python_version = current_file[len('requirements-'):-len('.txt')]
        extra_requires_key = ':python_version == "{}"'.format(python_version)
        extra_requires_dict[extra_requires_key] = parse_requirements(current_file)
    return extra_requires_dict


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    params['install_requires'] = parse_requirements('requirements.txt')
    params['test_suite'] = 'pytest'
    params['extras_require'].update(add_per_version_requirements())
    params['extras_require']['doc'] = parse_requirements('requirements-docs.txt')
    params['extras_require']['dev'] = parse_requirements('requirements-dev.txt')

setup(**params)
