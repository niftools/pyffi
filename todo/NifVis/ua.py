from pyffi.formats.nif import NifFormat
from OpenGL.GL import *


def GLNoLighting():
    glDisable( GL_LIGHTING )

def GLLighting():
    glEnable( GL_LIGHTING )


def SetPointSize( size ):
    glPointSize( size )

def SetLineWidth( width ):
    glLineWidth( width )

def SetColor( r, g, b, a = 1.0 ):
    glColor4f( r, g, b, a )

def SetColorA( color ):
    if not isinstance( color, tuple ): return
    if len( color ) == 3:
        SetColor( color[0], color[1], color[2] )
    elif len( color ) == 4:
        SetColor( color[0], color[1], color[2], color[3] )


def BeginDrawing( mode ):
    glBegin( mode )

def EndDrawing():
    glEnd()


def SetNormal( n ):
    glNormal3f( n.x, n.y, n.z )


def DrawVertex( v, mode = True ):
    if mode: glBegin( GL_POINTS )
    glVertex3f( v.x, v.y, v.z )
    if mode: glEnd()

def DrawVertices( verts, mode = True ):
    if mode: glBegin( GL_POINTS )
    for v in verts:
        DrawVertex( v, False )
    if mode: glEnd()

def DrawTriangle( t, verts, mode = True ):
    if mode: glBegin( GL_TRIANGLES )
    DrawVertex( verts[t.v1], False )
    DrawVertex( verts[t.v2], False )
    DrawVertex( verts[t.v3], False )
    if mode: glEnd()

def DrawTriangleW( t, verts, mode = True ):
    if mode: glBegin( GL_LINE_STRIP )
    DrawVertex( verts[t.v1], False )
    DrawVertex( verts[t.v2], False )
    DrawVertex( verts[t.v3], False )
    DrawVertex( verts[t.v1], False )
    if mode: glEnd()

def DrawTriangles( tris, verts, mode = True ):
    if mode: glBegin( GL_TRIANGLES )
    for t in tris:
        DrawTriangle( t, verts, False )
    if mode: glEnd()

def DrawTrianglesW( tris, verts, mode = True ):
    for t in tris:
        DrawTriangleW( t, verts, True )

def DrawLine( v, w, mode = True ):
    if mode: glBegin( GL_LINES )
    DrawVertex( v, False )
    DrawVertex( w, False )
    if mode: glEnd()

def DrawOffset( v, off ):
    w = NifFormat.Vector3()
    w.x = v.x + off.x
    w.y = v.y + off.y
    w.z = v.z + off.z
    DrawLine( v, w )
