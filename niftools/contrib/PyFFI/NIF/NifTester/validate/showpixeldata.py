"""Show image in NiPixelData block."""

from PyFFI.NIF import NifFormat
import os.path

try:
    from PIL import Image
    from PIL.ImageQt import ImageQt
except:
    Image = None


def testBlock(block, **args):
    # check if test applies
    if not isinstance(block, NifFormat.NiPixelData):
        return

    # check that PIL is installed
    if Image is None:
        print("""The showpixeldata test uses PIL.
Please install PIL from http://www.pythonware.com/products/pil/""")
        return

    # get image information
    mode, size, data = block.getRawImage()

    # display the image
    img = Image.fromstring(mode, size, data, "raw", mode, 0, 1)
    n = 0
    while True:
        filename = "image%03i.png" % n
        if not os.path.exists(filename):
            break
        n += 1
    img.save(filename)

