game = None

from enum import Enum
import pyglet
from world import World
from graphics import window
from agent import Agent  # Agent with seek, arrive, flee and pursuit

class Game():
	def __init__(self):
		self.world = World(window.size[0], window.size[1])
		# add one agent
		self.world.agents.append(Agent(self.world))
		# unpause the world ready for movement
		self.world.paused = False
  
		# labels
		window._update_label('mode', "Agents' Mode: seek")
		window._update_label('agents number', "Num of agents: {}".format(len(self.world.agents)))
		window._update_label('mass', "Agents' Mass: {}".format(self.world.agents[0].mass))
		window._update_label('max speed', "Agents' Max Speed: {}".format(self.world.agents[0].max_speed))

	def input_mouse(self, x, y, button, modifiers):
		self.world.input_mouse(x, y, button, modifiers)

	def input_keyboard(self, symbol, modifiers):
		self.world.input_keyboard(symbol, modifiers)

	def update(self, delta):
		self.world.update(delta)
  