from NifVis.ua import *

import random

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

    Scale = 1.0 * 255 * 255 / mopp.scalingFactor

    Corner = mopp.objectCorner

    ChunkCode( mopp.moppData, 0, len(mopp.moppData), Tree, verbose = True )

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

    xstep = 5
    ystep = 5
    zstep = 27

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
                if pos[0] <= chunk[1]:
                    DrawCode( pos, chunk[3], off, dim )
                if pos[0] <= chunk[2]:
                    return

            elif code == 0x11:
                if pos[1] <= chunk[1]:
                    DrawCode( pos, chunk[3], off, dim )
                if pos[1] <= chunk[2]:
                    return

            elif code == 0x12:
                if pos[2] <= chunk[1]:
                    DrawCode( pos, chunk[3], off, dim )
                if pos[2] <= chunk[2]:
                    return

            else:
                # cannot resolve further
                DrawCode( pos, chunk[3], off, dim )

##            elif code == 0x16:
##                if pos[1]*chunk[1] <= pos[2]*chunk[2]:
##                    DrawCode( pos, chunk[3], off, dim )
##                    return
##
##            elif code == 0x17:
##                if pos[2]*chunk[1] <= pos[0]*chunk[2]:
##                    DrawCode( pos, chunk[3], off, dim )
##                    return
##
##            elif code == 0x18:
##                if pos[0]*chunk[2] <= pos[1]*chunk[1]:
##                    DrawCode( pos, chunk[3], off, dim )
##                    return

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
            v.x = Corner.x + Scale * ( off[0] + pos[0] ) + random.uniform(0,0.1)
            v.y = Corner.y + Scale * ( off[1] + pos[1] ) + random.uniform(0,0.1)
            v.z = Corner.z + Scale * ( off[2] + pos[2] ) + random.uniform(0,0.1)

            SetColorA( Colors[(code-0x30)%len(Colors)] )

            DrawVertex( v )
            return

        else:
            print "WARNING: unknown code 0x%X"%code


def ChunkCode( bytes, index, length, tree, depth = 0, verbose = False ):
    stop = index + length
    while index < stop:
        code = bytes[index]
        chunk = ()
        jump = 1

        if code in range( 0x10, 0x20 ):
            if verbose:
                print "  "*depth, hex(code), bytes[index+1], bytes[index+2]
            subsize = bytes[index+3]
            subtree = ChunkCode( bytes, index+4, subsize, [], depth+1, verbose )
            chunk = ( code, bytes[index+1], bytes[index+2], subtree )
            jump = 4 + subsize

        elif code in range( 0x20, 0x30 ):
            if code in [ 0x26, 0x27, 0x28 ]:
                if verbose:
                    print "  "*depth, hex(code), bytes[index+1], bytes[index+2], "[%s-axis check]"%("XYZ"[code-0x26])
                chunk = ( code, bytes[index+1], bytes[index+2] )
                jump = 3
            else:
                if verbose:
                    print "  "*depth, hex(code), "(unknown)"

        elif code in range( 0x30, 0x4f ):
            if verbose:
                print "  "*depth, hex(code), "[triangle %i check]"%(code-0x30)
            chunk = ( bytes[index], 0 )
            jump = 1

        else:
            if verbose:
                print "  "*depth, hex(code), "(unknown)"

        tree.append( chunk )
        index += jump

    return tree
