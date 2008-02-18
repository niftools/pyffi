"""Show image in NiPixelData block."""

from PyFFI.NIF import NifFormat
from PyFFI.DDS import DdsFormat
import os.path

def testBlock(block, **args):
    # check if test applies
    if not isinstance(block, NifFormat.NiPixelData):
        return

    n = 0
    while True:
        filename = "image%03i.dds" % n
        if not os.path.exists(filename):
            break
        n += 1
    stream = open(filename, "wb")
    try:
        block.saveAsDDS(stream)
    finally:
        stream.close()
