from distutils.core import setup

setup(
    name = "pynif",
    version = "0.0",
    packages = ['FileFormat', 'FileFormat.Bases', 'NifFormat', 'NifFormat.PyTriStrip'],
    package_data = { '': ['*.xml' ] }, # include xml files
    author = "NIF File Format Library and Tools",
    author_email = "amorilia@gamebox.net",
    description = "A Python library for reading, writing, and processing nif files.",
    long_description = "A Python library for reading, writing, and processing nif files.",
    license = "BSD",
    keywords = "nif fileformat",
    url = "http://niftools.sourceforge.net/"
)
