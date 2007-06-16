# scale nif file

from NifFormat.NifFormat import NifFormat

def testRoot(root, verbose, arg = 1.0):
    root.applyScale(float(arg))

def testFile(version, user_version, f, roots, verbose, arg = 1.0):
    f.seek(0)
    NifFormat.write(version, user_version, f, roots)
