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

    for norm, tangents in izip(chunk.normalsData.normals,
                               chunk.tangentsData.tangents):
        norm = (norm.x, norm.y, norm.z)
        tan = tuple(x / 32767.0 for x in (tangents[0].x, tangents[0].y, tangents[0].z))
        bin = tuple(x / 32767.0 for x in (tangents[1].x, tangents[1].y, tangents[1].z))
        if abs(vecNorm(norm) - 1) > 0.001:
            print "WARNING: normal has non-unit norm"
        if abs(vecNorm(tan) - 1) > 0.001:
            print "WARNING: tangent has non-unit norm"
        if abs(vecNorm(bin) - 1) > 0.001:
            print "WARNING: binormal has non-unit norm"
        if (tangents[0].w != tangents[1].w):
            raise ValueError(
                "inconsistent tangent w coordinate (%i != %i)"
                % (tangents[0].w, tangents[1].w))
        if not (tangents[0].w in (-32767, 32767)):
            raise ValueError(
                "invalid tangent w coordinate (%i)" % tangents[0].w)
        if tangents[0].w > 0:
            cross = vecCrossProduct(tan, bin)
        else:
            cross = vecCrossProduct(bin, tan)
        crossnorm = vecNorm(cross)
        if abs(crossnorm - 1) > 0.001:
            # a lot of these...
            #print "WARNING: tan and bin not orthogonal"
            cross = vecscalarMul(cross, 1.0/crossnorm)
        if vecDistance(norm, cross) > 1:
            print "norm                 = %s" % (norm,)
            print "tan                  = %s" % (tan,)
            print "bin                  = %s" % (bin,)
            print "tan bin cross prod   = %s" % (cross,)
            print "error distance       = %f" % vecDistance(norm, cross)
            raise ValueError(
                "norm not cross product of tangent and binormal")
