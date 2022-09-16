import numpy as np
import pygame
from simulator import *

pygame.init()

DIM = (800, 800) # dimensions of the window
DELAY = 20 # time between consecutive frames
window = pygame.display.set_mode(DIM) 

pygame.display.set_caption("Simulation") # title of the window

# HOW TO USE

# 1. Define objects and set their properties with
# obj = Object(args)
# default arguments:    pos=[0,0]               initial position
#                       vel=[0,0]               initial velocity
#                       size=10                 radius 
#                       mass=10                 mass
#                       color=(200,200,200)     color on screen

# 2. Create a space containing the objects with
# space = Space(objects, dim)
# default arguments:
#                       objects (no default)    list of objects
#                       dim                     dimensions of window

# 3. In the main loop, update and draw the space with 
# space.update()
# space.draw(window)

# EXAMPLE:

balls = []
for i in range(100):
    ball = Object(np.array(DIM)*np.random.rand(2)) # object with uniformly random position
    theta = 2*np.pi*np.random.rand() #uniformly random direction
    ball.vel = 2*np.array([np.cos(theta), np.sin(theta)]) # set velocity in random direction
    ball.size = 8+18*(np.random.rand()**2) # set a random size 
    ball.mass = ball.size # set mass equal to the size 
    ball.color = (60+ball.size*7, 230-ball.size*3, 230-ball.size*3) # set color
    balls.append(ball)

space = Space(balls, DIM)


run = True

while run: 
    pygame.time.delay(DELAY) 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            run = False
    window.fill((40, 40, 40))
    space.update()
    space.draw(window)
            
    pygame.display.update()  
pygame.quit() 
