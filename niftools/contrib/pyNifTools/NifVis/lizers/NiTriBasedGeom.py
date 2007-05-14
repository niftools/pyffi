from NifFormat.NifFormat import NifFormat
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
    tris = mesh.triangles
        
    glColor3f( 1, 1, 1 )
    
    glBegin( GL_TRIANGLES )
    for t in tris:
        glNormal3f( norms[t.v1].x, norms[t.v1].y, norms[t.v1].z )
        glVertex3f( verts[t.v1].x, verts[t.v1].y, verts[t.v1].z )
        glNormal3f( norms[t.v2].x, norms[t.v2].y, norms[t.v2].z )
        glVertex3f( verts[t.v2].x, verts[t.v2].y, verts[t.v2].z )
        glNormal3f( norms[t.v3].x, norms[t.v3].y, norms[t.v3].z )
        glVertex3f( verts[t.v3].x, verts[t.v3].y, verts[t.v3].z )
    glEnd()
