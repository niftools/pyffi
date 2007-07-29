from distutils.core import setup

setup(
    name = "PyFFI",
    version = "0.2",
    packages = ['PyFFI', 'PyFFI.Bases', 'PyFFI.Utils', 'PyFFI.NIF'],
    package_data = { '' : [ '*.xml' ] }, # include xml files
    author = "Python File Format Interface",
    author_email = "amorilia@gamebox.net",
    description = "A Python library for reading, writing, and processing binary files.",
    long_description = "PyFFI reads a file format description (XML) and creates customizable Python classes to read & write such files (e.g. Netimmerse File Format (NIF), Crytek files (CGF)). Includes tools for files used by 3D games (e.g. stripifier, tangent space calculation). Only the NIF format is supported in this release.",
    license = "BSD",
    keywords = "fileformat nif cgf binary interface stripify",
    url = "http://pyffi.sourceforge.net/"
)
