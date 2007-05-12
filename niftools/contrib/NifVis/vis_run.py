import pygame
from pygame.locals import *

import vis_cfg



IsRunning = False



def EventHandler():
    global IsRunning
    
    events = pygame.event.get()
    for event in events: 
        if event.type == QUIT: 
            IsRunning = False
        else: 
            print event 



def Initialize():
    global IsRunning

    pygame.display.init()

    window = pygame.display.set_mode( ( vis_cfg._WINDOW_WIDTH, vis_cfg._WINDOW_HEIGHT ), OPENGL | DOUBLEBUF ) 
    pygame.display.set_caption( 'Nif Visualizer' ) 

    screen = pygame.display.get_surface()

    IsRunning = True
