from OpenGL.GL import *
from OpenGL.GLU import *

import pygame.display

import vis_cfg



Aspect = 4 / 3
Height = 480

Radius = 1

xRot = 0
yRot = 0
zRot = 0



def Initialize( radius ):
    global Radius, Aspect, Height

    Radius = radius

    Width = vis_cfg._WINDOW_WIDTH
    Height = min( vis_cfg._WINDOW_WIDTH, vis_cfg._WINDOW_HEIGHT )

    Aspect = 1.0 * Width / Height

    print "OpenGL Setup: Radius %.2f, Resolution %dx%d, Aspect %.2f" % ( Radius, Width, Height, Aspect )


def InitFrame():
    global Radius, Aspect, Height

    # Viewport
    glViewport( 0, ( vis_cfg._WINDOW_HEIGHT - Height ) / 2, vis_cfg._WINDOW_WIDTH, Height )

    # Initialize
    glClearColor( 0.5, 0.5, 0.5, 1 )

    glShadeModel( GL_SMOOTH )
    glEnable( GL_MULTISAMPLE_ARB )

    glClearDepth( 1 )
    glEnable( GL_DEPTH_TEST )
    glDepthFunc( GL_LEQUAL )

    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );

    glEnable( GL_ALPHA_TEST )
    glEnable( GL_BLEND )
    glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )

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

    # View translation
    glTranslatef( 0, 0, -Radius * 4 )

    # Set up light always from front
    glPushMatrix()
    glLoadIdentity()

    glLightfv( GL_LIGHT0,GL_POSITION,[ 0, 0, 0, 1 ] )

    glPopMatrix()

    # View rotation
    glRotatef( xRot, 1, 0, 0 )
    glRotatef( yRot, 0, 1, 0 )
    glRotatef( zRot, 0, 0, 1 )

    glRotatef( -90, 1, 0, 0 )



def FinalizeFrame():
    pygame.display.flip()


def InitDraw():
    glPushAttrib( GL_COLOR_BUFFER_BIT | GL_ENABLE_BIT | GL_POINT_BIT | GL_LINE_BIT )
    glPushMatrix()


def FinalizeDraw():
    glPopMatrix()
    glPopAttrib()


def RotateViewBy( xAngle, yAngle, zAngle ):
    global xRot, yRot, zRot

    xRot += xAngle
    yRot += yAngle
    zRot += zAngle

    NormalizeAngle( xAngle )
    NormalizeAngle( yAngle )
    NormalizeAngle( zAngle )



def RotateView( xAngle, yAngle, zAngle ):
    global xRot, yRot, zRot

    xRot = xAngle
    yRot = yAngle
    zRot = zAngle

    NormalizeAngle( xAngle )
    NormalizeAngle( yAngle )
    NormalizeAngle( zAngle )



def NormalizeAngle( angle ):
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360



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
