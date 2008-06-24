import pygame
from pygame.locals import *

import vis_cfg
import vis_gl



IsRunning = False



def EventHandler():
    global IsRunning

    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            IsRunning = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 2:
                vis_gl.RotateView( 0, 0, 0 )

        elif event.type == MOUSEMOTION:
            if event.buttons[0]:
                vis_gl.RotateViewBy( event.rel[1], event.rel[0], 0 )




def Initialize():
    global IsRunning

    pygame.display.init()

    window = pygame.display.set_mode( ( vis_cfg._WINDOW_WIDTH, vis_cfg._WINDOW_HEIGHT ), OPENGL | DOUBLEBUF )
    pygame.display.set_caption( 'Nif Visualizer' )

    screen = pygame.display.get_surface()

    IsRunning = True
