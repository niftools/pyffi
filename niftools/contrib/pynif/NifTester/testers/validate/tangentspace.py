# check tangent space calculation

from NifFormat.NifFormat import NifFormat

def testBlock(block, verbose):
    # does it apply on this block?
    if not isinstance(block, NifFormat.NiTriBasedGeom): return
    # does this block have tangent space data?
    for extra in block.getRefs():
        if isinstance(extra, NifFormat.NiBinaryExtraData):
            if extra.name == 'Tangent space (binormal & tangent vectors)':
                break
    else:
        return

    print 'found tangent space'
    # copy the tangent space data
    old_tangentspace = [b for b in extra.binaryData.data]
    # recalculate the tangent space
    block.updateTangentSpace()
    # copy the tangent space data
    new_tangentspace = [b for b in extra.binaryData.data]
    # compare the two spaces
    i = 0
    for old_b, new_b in zip(old_tangentspace, new_tangentspace):
        if old_b != new_b:
            print old_tangentspace
            print new_tangentspace
            raise ValueError('calculated tangent space differs from original at byte index %i'%i)
        i += 1
