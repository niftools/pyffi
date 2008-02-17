"""Show image in NiPixelData block."""

from PyFFI.NIF import NifFormat
from PyFFI.DDS import DdsFormat
import os.path

def testBlock(block, **args):
    # check if test applies
    if not isinstance(block, NifFormat.NiPixelData):
        return

    # export the image
    header = DdsFormat.Header()
    data = DdsFormat.PixelData()

    # uncompressed RGB(A)
    header.flags.caps = 1
    header.flags.height = 1
    header.flags.width = 1
    header.flags.pixelFormat = 1
    header.flags.mipmapCount = 1
    header.flags.linearSize = 1
    header.height = block.mipmaps[0].height
    header.width = block.mipmaps[0].width
    header.linearSize = len(block.pixelData)
    header.mipmapCount = len(block.mipmaps)
    header.pixelFormat.flags.rgb = 1
    header.pixelFormat.bitCount = block.bitsPerPixel
    header.pixelFormat.rMask = block.redMask
    header.pixelFormat.gMask = block.greenMask
    header.pixelFormat.bMask = block.blueMask
    header.pixelFormat.aMask = block.alphaMask
    header.caps1.complex = 1
    header.caps1.texture = 1
    header.caps1.mipmap = 1

    data.setValue(block.pixelData)

    n = 0
    while True:
        filename = "image%03i.dds" % n
        if not os.path.exists(filename):
            break
        n += 1
    stream = open(filename, "wb")
    try:
        DdsFormat.write(stream, version = 9, header = header, pixeldata = data)
    finally:
        stream.close()
