# writes back the file with single skeleton root and fix a single rest position

from PyFFI.Formats.NIF import NifFormat

__readonly__ = False

def testRoot(root, **args):
    verbose = args.get('verbose', 0)
    skelrootrefgeom = {}
    skingeoms = [geom for geom in root.tree() if isinstance(geom, NifFormat.NiGeometry) and geom.isSkin()]

    # first run: merge skeleton roots
    for geom in skingeoms:
        merged, failed = geom.mergeSkeletonRoots()
        if merged and verbose:
            print 'reparented following blocks to skeleton root of ' + geom.name + ':'
            print [node.name for node in merged]
        if failed:
            print 'WARNING: failed to reparented following blocks  to skeleton root of ' + geom.name + ':'
            print [node.name for node in failed]

    # second run: find reference geometries for each skeleton root, i.e. geometry with largest number of bones
    for geom in skingeoms:
        skelroot = geom.skinInstance.skeletonRoot
        numbones = len(geom.skinInstance.bones)
        if skelrootrefgeom.has_key(skelroot):
            if numbones > len(skelrootrefgeom[skelroot].skinInstance.bones):
                skelrootrefgeom[skelroot] = geom
        else:
            skelrootrefgeom[skelroot] = geom

    # third run: fix rest pose
    for skelroot, geom in skelrootrefgeom.iteritems():
        merged, failed = geom.mergeBoneRestPositions(force = True)
        if verbose:
            print 'fixing rest position of skeleton root ' + skelroot.name
        if merged and verbose:
            print 'merging rest position of ' + geom.name + ' with following geometries:'
            print [node.name for node in merged]
        if failed: # should not happen if force = True
            print 'WARNING: failed to merge rest position of ' + geom.name + ' with following geometries:'
            print [node.name for node in failed]
