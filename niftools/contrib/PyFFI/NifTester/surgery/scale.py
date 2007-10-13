# scale nif file

from PyFFI.NIF import NifFormat

def testRoot(root, **args):
    arg = args.get('arg', 1.0)
    root.applyScale(float(arg))

def testFile(version, user_version, f, roots, **args):
    f.seek(0)
    NifFormat.write(version, user_version, f, roots)
