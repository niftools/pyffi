from NifVis.ua import *

radius = 0.1

def Radius( block ):
    if not block: return
    if not isinstance( block, NifFormat.NiBinaryVoxelData ): return

    global radius

    verts = block.unknownVectors

    for v in verts:
        if v.w > radius: radius = v.w

    return radius


def Draw( block ):
    if not block: return
    if not isinstance( block, NifFormat.NiBinaryVoxelData ): return

    global radius

    GLNoLighting()

    SetPointSize( 4 )
    SetColor( 1, 1, 1 )

    DrawVertices( block.unknownVectors )

