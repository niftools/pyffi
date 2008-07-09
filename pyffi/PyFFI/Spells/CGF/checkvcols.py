"""Check if mesh has vertex colors."""

from PyFFI.Formats.CGF import CgfFormat

def testBlock(chunk, **kwargs):
    """Report whether mesh chunk has vertex colors."""
    if isinstance(chunk, CgfFormat.MeshChunk):
        if chunk.hasVertexColors:
            print "has vertex colors"
