# scale nif file

from PyFFI.NIF import NifFormat

__readonly__ = False

def testRoot(root, **args):
    arg = args.get('arg', 1.0)
    root.applyScale(float(arg))

