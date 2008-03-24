# check tangent space calculation

from PyFFI.CGF import CgfFormat
from PyFFI.Utils.MathUtils import *

from itertools import izip

def testChunk(chunk, **args):
    # check block type
    if not isinstance(chunk, CgfFormat.MeshChunk):
        return

    # get tangents and normals
    if not (chunk.normalsData and chunk.tangentsData):
        return

    oldtangents = [tangent for tangent in chunk.tangentsData.tangents]

    print "recalculating new tangent space"
    chunk.updateTangentSpace()
    newtangents = [tangent for tangent in chunk.tangentsData.tangents]

    print "validating and checking old with new"

    for norm, oldtangent, newtangent in izip(chunk.normalsData.normals,
                                             oldtangents, newtangents):
        print "*** %s ***" % (norm,)
        # check old
        norm = (norm.x, norm.y, norm.z)
        tan = tuple(x / 32767.0 for x in (oldtangent[0].x, oldtangent[0].y, oldtangent[0].z))
        bin = tuple(x / 32767.0 for x in (oldtangent[1].x, oldtangent[1].y, oldtangent[1].z))
        if abs(vecNorm(norm) - 1) > 0.001:
            print "WARNING: normal has non-unit norm"
        if abs(vecNorm(tan) - 1) > 0.001:
            print "WARNING: oldtangent has non-unit norm"
        if abs(vecNorm(bin) - 1) > 0.001:
            print "WARNING: binormal has non-unit norm"
        if (oldtangent[0].w != oldtangent[1].w):
            raise ValueError(
                "inconsistent oldtangent w coordinate (%i != %i)"
                % (oldtangent[0].w, oldtangent[1].w))
        if not (oldtangent[0].w in (-32767, 32767)):
            raise ValueError(
                "invalid oldtangent w coordinate (%i)" % oldtangent[0].w)
        if oldtangent[0].w > 0:
            cross = vecCrossProduct(tan, bin)
        else:
            cross = vecCrossProduct(bin, tan)
        crossnorm = vecNorm(cross)
        if abs(crossnorm - 1) > 0.001:
            # a lot of these...
            print "WARNING: tan and bin not orthogonal"
            print "         (error is %f)" % abs(crossnorm - 1)
            cross = vecscalarMul(cross, 1.0/crossnorm)
        if vecDistance(norm, cross) > 0.01:
            print "norm                 = %s" % (norm,)
            print "tan                  = %s" % (tan,)
            print "bin                  = %s" % (bin,)
            print "tan bin cross prod   = %s" % (cross,)
            print "error distance       = %f" % vecDistance(norm, cross)
            #raise ValueError(
            print(
                "WARNING: norm not cross product of tangent and binormal")

        # compare old with new
        if sum((abs(oldtangent[0].x - newtangent[0].x),
                abs(oldtangent[0].y - newtangent[0].y),
                abs(oldtangent[0].z - newtangent[0].z),
                abs(oldtangent[0].w - newtangent[0].w),
                abs(oldtangent[1].x - newtangent[1].x),
                abs(oldtangent[1].y - newtangent[1].y),
                abs(oldtangent[1].z - newtangent[1].z),
                abs(oldtangent[1].w - newtangent[1].w))) > 30000:
            if oldtangent[1].w == -32767:
                print "old tangent"
                print oldtangent[0], oldtangent[1]
                print "new tangent"
                print newtangent[0], newtangent[1]
            else:
                print "positive w..."
                print \
                    sum((abs(oldtangent[0].x - newtangent[0].x),
                         abs(oldtangent[0].y - newtangent[0].y),
                         abs(oldtangent[0].z - newtangent[0].z),
                         abs(oldtangent[0].w + newtangent[0].w),
                         abs(oldtangent[1].x - newtangent[1].x),
                         abs(oldtangent[1].y - newtangent[1].y),
                         abs(oldtangent[1].z - newtangent[1].z),
                         abs(oldtangent[1].w + newtangent[1].w)))
                
