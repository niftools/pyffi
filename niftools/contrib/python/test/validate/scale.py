# testing if applyScale propagates everything

from NifFormat.NifFormat import NifFormat

def testRoot(root, verbose):
    # bah, nothing to much here yet... so far only useful for profiling
    root.applyScale(10.0)
