import pyglet

from random import randrange

from vector2d import Vector2D
from graphics import COLOUR_NAMES, window
from world import World

class Obstacle(object):
    
    def __init__(self, world=None, x=200., y=200., radius=30.0):
        self.world = world
        self.pos = Vector2D(x, y)
        self.radius = radius
        
        self.circle = pyglet.shapes.Circle(
            x=self.pos.x, y=self.pos.y,
            radius=self.radius,
            color=COLOUR_NAMES['LIGHT_GREEN'],
            batch=window.get_batch("main")
        )
        
        self.target = pyglet.shapes.Circle(
            x=self.pos.x, y=self.pos.y,
            radius=5.0,
            color=COLOUR_NAMES['TRANSPARENT'],
            batch=window.get_batch("main")
        )
        
        self.circleEmphasize = pyglet.shapes.Circle(
            x=self.pos.x, y=self.pos.y,
            radius=self.radius,
            color=COLOUR_NAMES['TRANSPARENT'],
            batch=window.get_batch("main")
        )
        
    def isSafe(self):
        
        hunter = self.world.hunter
        
        safeDistance = 100 + self.radius * 2
        
        from_hunter = self.pos - hunter.pos
        distance = from_hunter.length()
        
        isSafe = distance > safeDistance
        
        if isSafe:
            self.circle.color = COLOUR_NAMES['LIGHT_GREEN']
        else:
            self.circle.color = COLOUR_NAMES['DARK_GREEN']
            
        return isSafe
            
    def update(self, delta):
        self.isSafe()
        
    def reset(self, world):
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))