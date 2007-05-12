from OpenGL.GL import *
from OpenGL.GLU import *

import pygame.display

import vis_cfg



Aspect = 4 / 3
Height = 480

Radius = 1



def Initialize( radius ):
    global Radius, Aspect, Height
    
    Radius = radius
    
    Height = min( vis_cfg._WINDOW_WIDTH, vis_cfg._WINDOW_HEIGHT )
    
    Aspect = vis_cfg._WINDOW_WIDTH / Height
    
    

def InitFrame():
    global Radius, Aspect, Height
    
    # Viewport
    glViewport( 0, ( vis_cfg._WINDOW_HEIGHT - Height ) / 2, vis_cfg._WINDOW_WIDTH, Height )

    # Initialize
    glClearColor( 0.8, 0.8, 0.9, 0 )
    
    glShadeModel( GL_SMOOTH )
    
    glClearDepth( 1 )
    glEnable( GL_DEPTH_TEST )
    glDepthFunc( GL_LEQUAL )
    
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
    
    # Light source
    glLightfv( GL_LIGHT0,GL_AMBIENT,[ .5, .5, .5, 1. ] )
    glLightfv( GL_LIGHT0,GL_DIFFUSE,[ .8, .8, .8, 1. ] )
    glLightfv( GL_LIGHT0,GL_SPECULAR,[ 1., 1., 1., 1. ] )
    glEnable( GL_LIGHT0 )
    glEnable( GL_LIGHTING )

    # Projection
    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()
    gluPerspective ( 45, Aspect, 0.1, -Radius * 2 )

    # Initialize ModelView matrix
    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    # View transformation
    glTranslatef( 0, 0, -Radius * 4 )
    
    
    
def Lighting():
    glPushMatrix()
    glLoadIdentity()
    
    glLightfv( GL_LIGHT0,GL_POSITION,[ 0, 0, 0, 1 ] )
    
    glPopMatrix()



def FinalizeFrame():
    pygame.display.flip()



def DrawAxes():
    global Radius
        
    glDisable( GL_LIGHTING )
    
    glPushMatrix()
    
    axis = Radius * 1.2
    arrow = Radius / 36.0
    
    glBegin( GL_LINES )
    
    glColor3f( 1.0, 0.0, 0.0 )
    glVertex3f( - axis, 0, 0 )
    glVertex3f( + axis, 0, 0 )
    glVertex3f( + axis, 0, 0 )
    glVertex3f( + axis - 3 * arrow, + arrow, + arrow )
    glVertex3f( + axis, 0, 0 )
    glVertex3f( + axis - 3 * arrow, - arrow, + arrow )
    glVertex3f( + axis, 0, 0 )
    glVertex3f( + axis - 3 * arrow, + arrow, - arrow )
    glVertex3f( + axis, 0, 0 )
    glVertex3f( + axis - 3 * arrow, - arrow, - arrow )
    glColor3f( 0.0, 1.0, 0.0 )
    glVertex3f( 0, - axis, 0 )
    glVertex3f( 0, + axis, 0 )
    glVertex3f( 0, + axis, 0 )
    glVertex3f( + arrow, + axis - 3 * arrow, + arrow )
    glVertex3f( 0, + axis, 0 )
    glVertex3f( - arrow, + axis - 3 * arrow, + arrow )
    glVertex3f( 0, + axis, 0 )
    glVertex3f( + arrow, + axis - 3 * arrow, - arrow )
    glVertex3f( 0, + axis, 0 )
    glVertex3f( - arrow, + axis - 3 * arrow, - arrow )
    glColor3f( 0.0, 0.0, 1.0 )
    glVertex3f( 0, 0, - axis )
    glVertex3f( 0, 0, + axis )
    glVertex3f( 0, 0, + axis )
    glVertex3f( + arrow, + arrow, + axis - 3 * arrow )
    glVertex3f( 0, 0, + axis )
    glVertex3f( - arrow, + arrow, + axis - 3 * arrow )
    glVertex3f( 0, 0, + axis )
    glVertex3f( + arrow, - arrow, + axis - 3 * arrow )
    glVertex3f( 0, 0, + axis )
    glVertex3f( - arrow, - arrow, + axis - 3 * arrow )
    glEnd()
    
    glPopMatrix()
    
    glEnable( GL_LIGHTING )
