from pyffi.formats.nif import NifFormat
from OpenGL.GL import *

def Radius( block ):
    if not block: return
    if not isinstance( block, NifFormat.NiTriBasedGeom ): return 0

    mesh = block.data
    if not mesh: return 0

    return mesh.radius

def Draw( block ):
    if not block: return
    if not isinstance( block, NifFormat.NiTriBasedGeom ): return

    mesh = block.data
    if not mesh: return

    verts = mesh.vertices
    norms = mesh.normals
    tris = mesh.getTriangles()

    glColor3f( 1, 1, 1 )

    glBegin( GL_TRIANGLES )
    for v1, v2, v3 in tris:
        glNormal3f( norms[v1].x, norms[v1].y, norms[v1].z )
        glVertex3f( verts[v1].x, verts[v1].y, verts[v1].z )
        glNormal3f( norms[v2].x, norms[v2].y, norms[v2].z )
        glVertex3f( verts[v2].x, verts[v2].y, verts[v2].z )
        glNormal3f( norms[v3].x, norms[v3].y, norms[v3].z )
        glVertex3f( verts[v3].x, verts[v3].y, verts[v3].z )
    glEnd()
