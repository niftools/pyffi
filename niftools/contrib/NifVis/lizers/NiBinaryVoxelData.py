from NifFormat.NifFormat import NifFormat
from OpenGL.GL import *

import sys

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
    
    glDisable( GL_LIGHTING )
    
    glPointSize( 4 )
    glColor4f( 1, 1, 1, 1 )
    
    verts = block.unknownVectors
    
    glBegin( GL_POINTS )
    for v in verts:
        glVertex3f( v.x * v.w, v.y * v.w, v.z * v.w )
    glEnd()
