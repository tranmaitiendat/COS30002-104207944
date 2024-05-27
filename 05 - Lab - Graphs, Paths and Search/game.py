game = None

from enum import Enum

import pyglet
from box_world import BoxWorld
from graphics import window

# Mouse mode indicates what the mouse "click" should do...
class MouseModes(Enum):
	CLEAR = 	pyglet.window.key._1
	MUD = 		pyglet.window.key._2
	WATER = 	pyglet.window.key._3
	FOREST =    pyglet.window.key._4
	ICE = 		pyglet.window.key._5
	WALL = 		pyglet.window.key._6
	# START = 	pyglet.window.key._7
	TARGET = 	pyglet.window.key._8

class Game():
	def __init__(self, map):
     
		self.world = BoxWorld.FromFile(map)
  
		self.currentAgent = self.world.agents[0]
  
		# Mouse mode indicates what the mouse "click" should do...
		self.mouseMode = MouseModes.MUD
		window._update_label('mouse', 'Click to place: '+ self.mouseMode.name)

		window._update_label('search', 'Search Type: A*')
  
		# Search limit
		# (0 means unlimited)
		self.searchLimit = 0
		self.updateLimitDisplay()
  
		window._update_label('status', 'Status: Loaded')

		window._update_label('agent', 'Current Agent: '+ self.currentAgent.name)

	
	def planPath(self):
		self.world.planPath(agent=self.currentAgent, limit=self.searchLimit)
		window._update_label('status', 'Status: Path Planned')
  
	def moveAgent(self):
		self.world.moveAgent(agent=self.currentAgent)
  
	def updateLimitDisplay(self):
		if (self.searchLimit >= 1):
			window._update_label('limit', 'Limit: %d' % self.searchLimit)
		else:
			window._update_label('limit', 'Limit: None')

	def input_mouse(self, x, y, button, modifiers):
		box = self.world.getBoxByPos(x, y)
		if box:
			if self.mouseMode == MouseModes.TARGET:
				self.world.setTarget(box.node.idx)
				self.planPath()
			else:
				box.setType(self.mouseMode.name)
			self.world.resetNavGraph()
			self.planPath()
			self.world.resetAgent(agent=self.currentAgent)
			window._update_label('status','Status: Graph Changed')

	def input_keyboard(self, symbol, modifiers):
		# Mode change?
		if symbol in MouseModes:
			self.mouseMode = MouseModes(symbol)
			window._update_label('mouse', 'Click to place: '+ self.mouseMode.name)

		# Plan a path 
		elif symbol == pyglet.window.key.SPACE:
			self.planPath()
   
		# Update the search limit
		elif symbol == pyglet.window.key.UP:
			self.searchLimit += 1
			self.updateLimitDisplay()
			self.world.resetAgent(agent=self.currentAgent)
			self.planPath()
		elif symbol == pyglet.window.key.DOWN:
			if self.searchLimit >= 1:
				self.searchLimit -= 1
				self.updateLimitDisplay()
				self.world.resetAgent(agent=self.currentAgent)
				self.planPath()
    
		# Update the current agent
		# FAST_HUNTER
		elif symbol == pyglet.window.key.A:
			self.currentAgent = self.world.agents[0]
			self.planPath()
			window._update_label('agent', 'Current Agent: '+ self.currentAgent.name)
		# SLOW_HUNTER
		elif symbol == pyglet.window.key.S:
			self.currentAgent = self.world.agents[1]
			self.planPath()
			window._update_label('agent', 'Current Agent: '+ self.currentAgent.name)
		# FAST_PREY
		elif symbol == pyglet.window.key.D:
			self.currentAgent = self.world.agents[2]
			self.planPath()
			window._update_label('agent', 'Current Agent: '+ self.currentAgent.name)
		# SLOW_PREY
		elif symbol == pyglet.window.key.W:
			self.currentAgent = self.world.agents[3]
			self.planPath()
			window._update_label('agent', 'Current Agent: '+ self.currentAgent.name)
   
		# Move agent
		elif symbol == pyglet.window.key.F:
			self.moveAgent()