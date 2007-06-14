# writes back the file with single skeleton root and fix a single rest position

from NifFormat.NifFormat import NifFormat

def testRoot(root, verbose):
    skelrootrefgeom = {}

    # first run: merge skeleton roots
    for geom in root.tree():
        if not isinstance(geom, NifFormat.NiGeometry): continue
        if not geom.isSkin(): continue
        merged, failed = geom.mergeSkeletonRoots()
        if merged:
            print
            print 'reparented following blocks to skeleton root of ' + geom.name + ':'
            print [node.name for node in merged]
        if failed:
            print 'WARNING: failed to reparented following blocks ' + geom.name + ':'
            print [node.name for node in failed]

    # second run: find reference geometries for each skeleton root, i.e. geometry with largest number of bones
    for geom in root.tree():
        if not isinstance(geom, NifFormat.NiGeometry): continue
        if not geom.isSkin(): continue
        skelroot = geom.skinInstance.skeletonRoot
        numbones = len(geom.skinInstance.bones)
        if skelrootrefgeom.has_key(skelroot):
            if numbones > len(skelrootrefgeom[skelroot].skinInstance.bones):
                skelrootrefgeom[skelroot] = geom
        else:
            skelrootrefgeom[skelroot] = geom

    # thid run: fix rest pose
    for skelroot, geom in skelrootrefgeom.iteritems():
        merged, failed = geom.mergeBoneRestPositions(force = True)
        print
        print 'fixing rest position of skeleton root ' + skelroot.name
        if merged:
            print 'merging rest position of ' + geom.name + ' with following geometries:'
            print [node.name for node in merged]
        if failed: # should not happen if force = True
            print 'WARNING: failed to merge rest position of ' + geom.name + ' with following geometries:'
            print [node.name for node in failed]

def testFile(version, user_version, f, roots, verbose):
    # write result
    print "writing file"
    f.seek(0)
    NifFormat.write(version, user_version, f, roots)
    print
