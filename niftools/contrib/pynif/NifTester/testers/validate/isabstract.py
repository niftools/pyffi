# checks for abstract blocks

from PyFFI.NIF import NifFormat

def testBlock(block, verbose):
    if block._isAbstract:
        raise ValueError('block %s marked as abstract in xml but used in nif file'%block.__class__.__name__)
