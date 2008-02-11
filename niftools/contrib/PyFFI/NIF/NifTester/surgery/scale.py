# scale nif file

from PyFFI.NIF import NifFormat

def testRoot(root, **args):
    arg = args.get('arg', 1.0)
    root.applyScale(float(arg))

