import numpy as np
import pygame

# a 2d physics simulation framework for elastic collisions between circles

# ELASTIC COLLISIONS OF MULTIPLE CIRCLES WITH QUADTREES by Nicolas Ruan
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


QUADTREE_K = 5 # max number of objects per leaf of quadtree


def inside(pos, size, objects):
    # returns subset of objects that lie at least partially within a rectangle
    # pos: upper-left corner of rectangle
    # size: width and height of rectangle
    # objects: list of objects
    x,y = pos
    w, h = size
    P = []
    for obj in objects:
        p = obj.pos
        s = obj.size
        if x <= p[0] + s and p[0]-s < x+w and y <= p[1]+s and p[1]-s < y+h:
            P.append(obj)
    return P


def recursive_subdivide(node, k):
    # recursively divides nodes into four quadrants
    # until each node contains at most k objects 
    if len(node.points)<=k:
        return

    size = node.size/2
    p = inside(node.pos, node.size, node.points)
    x1 = Node(node.pos, size, p)
    recursive_subdivide(x1, k)

    x = node.pos[0] + size[0]
    y = node.pos[1]
    p = inside(np.array([x,y]), size, node.points)
    x2 = Node(np.array([x,y]), size, p)
    recursive_subdivide(x2, k)

    x = node.pos[0]
    y = node.pos[1]+ size[1]
    p = inside(np.array([x,y]), size, node.points)
    x3 = Node(np.array([x,y]), size, p)
    recursive_subdivide(x3, k)

    x = node.pos[0] + size[0]
    y = node.pos[1]+ size[1]
    p = inside(np.array([x,y]), size, node.points)
    x4 = Node(np.array([x,y]), size, p)
    recursive_subdivide(x4, k)
    node.children = [x1, x2, x3, x4]
    node.points = []


class Object: # a circular object in 2d space
    def __init__(self, pos=[0, 0], size=10, vel=[0,0], mass=10, color=(200, 200, 200)):
        self.pos = np.array(pos) # position vector of center
        self.vel = np.array(vel) # velocity vector
        self.size = size # radius
        self.color = color 
        self.mass = mass

    def dist(self, other):
        return np.linalg.norm(self.pos - other.pos)

    def collides(self, other):
        # return True if objects collide (intersecting or touching) 
        return self.dist(other) <= self.size + other.size

    def draw(self, window):
        pygame.draw.circle(window, self.color, self.pos, self.size) 
  


class Node: # a node of the quadtree
    def __init__(self, pos=[0,0], size = np.array([400, 400]), points=[]):
        self.pos = np.array(pos) # upper-left corner of quadrant
        self.size = size # width and height of quadrant
        self.points=points # objects that lie inside quadrant
        self.children = [] 

class Collision: # a collision between two objects
    def __init__(self, obj1, obj2):
        self.obj1 = obj1
        self.obj2 = obj2

    def __eq__(self, other):
        return (self.obj1 == other.obj1 and self.obj2 == other.obj2) or (self.obj1 == other.obj2 and self.obj2 == other.obj1)


class Space: 
    def __init__(self, objects, dim=(800, 800)):
        self.objects = objects
        self.dim = np.array(dim)
        self.collisions = list()
        
    def traverse(self,node):
        # traverse the tree top-to-bottom and
        # detect collisions within each leaf
        if not node.children:
            for obj in node.points:
                for obj2 in node.points:
                    coll = Collision(obj, obj2)
                    if obj != obj2 and obj.collides(obj2) and not coll in self.collisions:  
                        self.collisions.append(coll)
                        
        else:
            for child in node.children:
                self.traverse(child)

        del node 


    def find_collisions(self):
        # finds all collisions between pairs of objects
        # 1. initialize a root with a rectangle that covers the space
        root = Node(pos=[0, 0], size = self.dim, points = self.objects)
        # 2. recursively divide node into four nodes if the rectangle of
        #    the node contains more than QUADTREE_K objects
        recursive_subdivide(root, QUADTREE_K)
        # 3. traverse the tree and store collisions
        self.traverse(root)
        return self.collisions

    def draw(self, window):
        # draws all objects in the space
        for obj in self.objects:
            obj.draw(window)
    
    def handle_collisions(self):
        # updates the positions and velocities of colliding particles
        self.find_collisions()
        for c in self.collisions:
            obj = c.obj1
            obj2 = c.obj2
            
            diff = obj2.pos-obj.pos #difference vector of positions
            v = diff/np.linalg.norm(diff) # normalized difference vector 
            ol = (obj.size + obj2.size - obj2.dist(obj))/2 # half the overlapping length

            # reposition such that objects are touching instead of overlapping
            obj.pos = obj.pos - ol * v 
            obj2.pos = obj2.pos + ol*v

            # rotate velocities so that the objects lie on the x-axis
            theta = np.arctan2(-diff[1], diff[0])
            rot = np.array([[np.cos(theta), -np.sin(theta)],
                                  [np.sin(theta), np.cos(theta)]])
            obj.vel = np.matmul(rot, obj.vel)
            obj2.vel =  np.matmul(rot, obj2.vel)

            # apply conservation of momentum and conservation of energy in 1D along x-axis
            m = obj.mass + obj2.mass
            vf1 = ((obj.mass - obj2.mass)*obj.vel[0] + 2*obj2.mass*obj2.vel[0])/m
            vf2 = ((obj2.mass - obj.mass)*obj2.vel[0] + 2*obj.mass*obj.vel[0])/m
            obj.vel[0] = vf1
            obj2.vel[0] = vf2

            # rotate velocities to the original basis
            invrot = np.transpose(rot)
            obj.vel = np.matmul(invrot, obj.vel)
            obj2.vel = np.matmul(invrot, obj2.vel)

            # remove the collision object
            self.collisions.remove(c)
            del c


    def move_objects(self):
        for obj in self.objects:
            # move object 
            obj.pos = obj.pos + obj.vel
            x,y = obj.pos
            # ensure that position is and stays within bounds 
            if y >= self.dim[1]-obj.size:
                obj.pos[1]= self.dim[1]-obj.size
                obj.vel[1]= min(0, -obj.vel[1])

            if x <= obj.size:
                obj.pos[0]=obj.size
                obj.vel[0] = max(0, -obj.vel[0])

            if x >= self.dim[0]-obj.size:
                obj.pos[0]=self.dim[0]-obj.size
                obj.vel[0] = min(0, -obj.vel[0])

            if y <= obj.size:
                obj.pos[1] = obj.size
                obj.vel[1] = max(0, -obj.vel[1])
                

    def update(self):
        self.move_objects()
        self.handle_collisions()
