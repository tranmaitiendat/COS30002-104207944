game = None

from enum import Enum
import pyglet
from world import World
from graphics import window
from agent import *
from obstacle import Obstacle

class Game():
	def __init__(self):
		self.world = World(window.size[0], window.size[1])
  
		self.world.obstacles = [
			Obstacle(self.world), 
			Obstacle(self.world, x=400., y=400., radius=40.), 
			Obstacle(self.world, x=600., y=200., radius=20.),
			Obstacle(self.world, x=200., y=700., radius=20.),
			Obstacle(self.world, x=700., y=700., radius=25.)]
        
	def input_mouse(self, x, y, button, modifiers):
		self.world.input_mouse(x, y, button, modifiers)

	def input_keyboard(self, symbol, modifiers):
		self.world.input_keyboard(symbol, modifiers)

	def update(self, delta):
		self.world.update(delta)