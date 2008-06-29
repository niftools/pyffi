from NifVis.ua import *

Scale = 0.1
Corner = NifFormat.Vector3()
Tree = []

Colors = [
    ( 1, 0, 0 ),
    ( 0, 1, 0 ),
    ( 0, 0, 1 ),
    ( 1, 1, 0 ),
    ( 0, 1, 1 ),
    ( 1, 0, 1 ),
    ( 1, 0.75, 0 ),
    ( 0, 1, 0.75 ),
    ( 0.75, 0, 1 )
]

def Radius( mopp ):
    if not mopp: return
    if not isinstance( mopp, NifFormat.bhkMoppBvTreeShape ): return

    global Scale, Corner, Tree

    Scale = 1.0 * 255 * 255 / mopp.scale

    Corner = mopp.origin

    ChunkCode( mopp.moppData, 0, len(mopp.moppData), Tree )

    print "Scale: %.3f - Corner: (%.2f, %.2f, %.2f )" % ( Scale, Corner.x, Corner.y, Corner.z )

    return ( 0.5 * Scale * 255 )


def Draw( mopp ):
    if not mopp: return
    if not isinstance( mopp, NifFormat.bhkMoppBvTreeShape ): return

    global Tree, Colors


    GLNoLighting()


    SetLineWidth( 1 )

    SetColor( 1, 1, 1, 0.2 )

    Shape = mopp.shape.data
    tris = Shape.triangles
    verts = Shape.vertices

    colnum = 0
    for t in tris:
        SetColorA( Colors[colnum%len(Colors)] )
        SetNormal( t.normal )
        DrawTriangleW( t.triangle, verts )
        colnum += 1


    SetPointSize( 4 )
    SetLineWidth( 3 )

    xstep = 8
    ystep = 8
    zstep = 128

    x = 0
    while x < 256:
        y = 0
        while y < 256:
            z = 0
            while z < 256:
                DrawCode( ( x, y, z ), Tree, [ 0, 0, 0 ], [ 0, 0, 0 ] )
                z += zstep
            y += ystep
        x += xstep


def DrawCode( pos, tree, off, dim ):
    global Scale, Corner

    for chunk in tree:
        code = chunk[0]

        if code in range( 0x10, 0x20 ):
            if code == 0x10:
                a = (1.0 * (pos[0]+1) / (chunk[1]+1))
                b = (1.0 * (chunk[2]+1) / (pos[0]+1))
                if a < b:
                    DrawCode( pos, chunk[3], off, dim )
                    return

            elif code == 0x11:
                a = (1.0 * (pos[1]+1) / (chunk[1]+1))
                b = (1.0 * (chunk[2]+1) / (pos[1]+1))
                if a < b:
                    DrawCode( pos, chunk[3], off, dim )
                    return

            elif code == 0x17:
                a = (1.0 * (dim[0]-pos[0]+1) / (pos[1]+1))
                b = (1.0 * (chunk[2]+1) / (chunk[1]+1))
                if a > b:
                    DrawCode( pos, chunk[3], off, dim )
                    return

            elif code == 0x18:
                a = (1.0 * (chunk[2]+1) / (chunk[1]+1))
                b = (1.0 * (pos[0]+1) / (pos[1]+1))
                if a > b:
                    DrawCode( pos, chunk[3], off, dim )
                    return

        elif code in range( 0x20, 0x30 ):
            if code == 0x26:
                if pos[0] < chunk[1] or pos[0] > chunk[2]:
                    return
                dim[0] = chunk[2]

            elif code == 0x27:
                if pos[1] < chunk[1] or pos[1] > chunk[2]:
                    return
                dim[1] = chunk[2]

            elif code == 0x28:
                if pos[2] < chunk[1] or pos[2] > chunk[2]:
                    return
                dim[2] = chunk[2]

        elif code in range( 0x30, 0x50 ):
            v = NifFormat.Vector3()
            v.x = Corner.x + Scale * ( off[0] + pos[0] )
            v.y = Corner.y + Scale * ( off[1] + pos[1] )
            v.z = Corner.z + Scale * ( off[2] + pos[2] )

            SetColorA( Colors[(code-0x30)%len(Colors)] )

            DrawVertex( v )
            return


def ChunkCode( bytes, index, length, tree ):
    stop = index + length
    while index < stop:
        code = bytes[index]
        chunk = ()
        jump = 1

        if code in range( 0x10, 0x20 ):
            subsize = bytes[index+3]
            subtree = ChunkCode( bytes, index+4, subsize, [] )
            chunk = ( code, bytes[index+1], bytes[index+2], subtree )
            jump = 4 + subsize

        elif code in range( 0x20, 0x30 ):
            if code in [ 0x26, 0x27, 0x28 ]:
                chunk = ( code, bytes[index+1], bytes[index+2] )
                jump = 3

        elif code in range( 0x30, 0x4f ):
            chunk = ( bytes[index], 0 )
            jump = 1

        tree.append( chunk )
        index += jump

    return tree
