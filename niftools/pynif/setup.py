import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "pynif",
    version = "0.0",
    packages = find_packages(exclude = ['NifFormat.NvTriStrip', 'rundoctest.py', 'runtest_old.py', 'examples']),
    package_data = { '': ['*.xml' ] }, # include xml files
    author = "NIF File Format Library and Tools",
    description = "A Python library for reading, writing, and processing nif files.",
    license = "BSD",
    keywords = "nif fileformat",
    url = "http://niftools.sourceforge.net/"
)
