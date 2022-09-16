# elastic-collisions-2d
# a 2d physics simulation framework for elastic collisions between multiple circular hitboxes
# constructs quadtrees to avoid redundant checks
# uses pygame for drawing on screen

# HOW TO USE 
# (see example.py)
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

# HOW IT WORKS 
# Constructing a quadtree
#   1. start with a root node that stores a rectangle covering the entire space
#   2. recursively divide the rectangle into four quadrants (i.e. rectangles)
#      until each quadrant contains at most k objects
#
# Detecting collisions
#   1. traverse the tree breadth-first
#   2. detect all pairwise collisions within quadrants associated with leaves
#      by testing if the distance between the objects is less than or equal to the sum of radii
#
# Handling collisions
#   1. for each pair of objects that collide:
#   2.    change basis such that object positions are aligned along the x-axis
#         (the transformation is a rotation by atan(dy/dx) radians
#         where (dx, dy) is the difference vector of object positions)
#   4.    move objects away from eachother so they do not overlap
#   5.    apply the laws of conservation of momentum and conservation of energy
#         in 1D to the first component of the velocity vectors
#   6.    change basis back to original (rotation matrix is orthogonal so use transpose matrix for the inverse transformation)
