game = None

from enum import Enum
import pyglet
from world import World
from graphics import window
from agent import Agent

class Game():
	def __init__(self):
		self.world = World(window.size[0], window.size[1])

	def input_mouse(self, x, y, button, modifiers):
		self.world.input_mouse(x, y, button, modifiers)

	def input_keyboard(self, symbol, modifiers):
		self.world.input_keyboard(symbol, modifiers)

	def update(self, delta):
		self.world.update(delta)