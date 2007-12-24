# check if mesh has vertex colors

from PyFFI.CGF import CgfFormat

def testChunk(chunk, **kwargs):
    if isinstance(chunk, CgfFormat.MeshChunk):
        if chunk.hasVertexColors:
            print "has vertex colors"
