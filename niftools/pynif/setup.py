from setuptools import setup, find_packages

setup(
    name = "pynif",
    version = "0.0",
    packages = find_packages(exclude = ['NifFormat.NvTriStrip', 'rundoctest.py', 'runtest_old.py', 'examples']),
    package_data = { '': ['*.xml' ] }, # include xml files
    url = "http://niftools.sourceforge.net/"
)
