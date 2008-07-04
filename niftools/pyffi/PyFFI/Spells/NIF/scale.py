"""Scale nif file."""

from PyFFI.Formats.NIF import NifFormat

__readonly__ = False

def testRoot(root, **args):
    """Apply scale on the tree.

    @param root: The root of the tree to scale.
    @type root: L{NifFormat.NiObject}
    """
    arg = args.get('arg', 1.0)
    root.applyScale(float(arg))

