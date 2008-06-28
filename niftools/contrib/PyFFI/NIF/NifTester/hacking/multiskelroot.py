# checks whether all skinned geometries have the same skeleton root
# morrowind nifs that test positive on this are as follows

# bip01 and left and right upper arm skeleton roots:
# r/azura.nif
# r/skeleton.nif
# r/lordvivec.nif

# bone root and scene root:
# r/cliffracer.nif

# bip01, neck, and spine01:
# r/dwarvenspecter.nif

from PyFFI.Formats.NIF import NifFormat

def testRoot(root, **args):
    skelroots = set()
    for block in root.tree():
        if isinstance(block, NifFormat.NiSkinInstance):
            skelroots.add(block.skeletonRoot)

    if len(skelroots) >= 2:
        print "multiple skeleton roots detected"
        for skelroot in skelroots:
            print skelroot.name
