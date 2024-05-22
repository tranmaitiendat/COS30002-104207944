'''A 2d world that supports preys with steering behaviour

Created for COS30002 AI for Games, by Clinton Woodward <cwoodward@swin.edu.au>
For class use only. Do not publically share or post this code without permission.

'''

from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from graphics import COLOUR_NAMES, window
from agent import Agent

class World(object):
	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
		self.agents = [Agent(self)]
		self.agents[0].isChosen = True
  
		self.chosenIndex = 0
  
		self.paused = False
		self.showinfo = True
  
		self.worldMode = "Wandering"

	def update(self, delta):
     
		if not self.paused:

			for agent in self.agents:
				agent.update(delta)	
    
			window._update_label("world mode", "World mode: {}".format(self.worldMode))	
			window._update_label("agents number", "Agents' number: {}".format(len(self.agents)))	
			window._update_label("chosen index", "Chosen agent index: {}".format(self.chosenIndex))	
			window._update_label("chosen near range", "Chosen agent's near range: {}".format(self.agents[self.chosenIndex].nearRange))	
			window._update_label("chosen far range", "Chosen agent's near range: {}".format(self.agents[self.chosenIndex].farRange))	
   
	def wrap_around(self, pos):
		''' Treat world as a toroidal space. Updates parameter object pos '''
		max_x, max_y = self.cx, self.cy
		if pos.x > max_x:
			pos.x = pos.x - max_x
		elif pos.x < 0:
			pos.x = max_x - pos.x
		if pos.y > max_y:
			pos.y = pos.y - max_y
		elif pos.y < 0:
			pos.y = max_y - pos.y

	def transform_points(self, points, pos, forward, side, scale):
		''' Transform the given list of points, using the provided position,
			direction and scale, to object world space. '''
		# make a copy of original points (so we don't trash them)
		wld_pts = [pt.copy() for pt in points]
		# create a transformation matrix to perform the operations
		mat = Matrix33()
		# scale,
		mat.scale_update(scale.x, scale.y)
		# rotate
		mat.rotate_by_vectors_update(forward, side)
		# and translate
		mat.translate_update(pos.x, pos.y)
		# now transform all the points (vertices)
		mat.transform_vector2d_list(wld_pts)
		# done
		return wld_pts

	def transform_point(self, point, pos, forward, side):
		''' Transform the given single point, using the provided position,
		and direction (forward and side unit vectors), to object world space. '''
		# make a copy of the original point (so we don't trash it)
		world_pt = point.copy()
		# create a transformation matrix to perform the operations
		mat = Matrix33()
		# rotate
		mat.rotate_by_vectors_update(forward, side)
		# and translate
		mat.translate_update(pos.x, pos.y)
		# now transform the point (in place)
		mat.transform_vector2d(world_pt)
		# done
		return world_pt
	
	def input_keyboard(self, symbol, modifiers):
     
		if symbol == pyglet.window.key.P:
			self.paused = not self.paused
   
		elif symbol == pyglet.window.key.A:
			newAgent = Agent(self, mode=self.worldMode)
			self.agents.append(newAgent)
   
		elif symbol == pyglet.window.key.UP:
			if self.chosenIndex < len(self.agents) - 1:
				self.chosenIndex += 1
			else:
				self.chosenIndex = 0
    
			self.updateChosenAgent()  
    
		elif symbol == pyglet.window.key.DOWN:
			if self.chosenIndex > 0:
				self.chosenIndex -= 1
			else:
				self.chosenIndex = len(self.agents) - 1
    
			self.updateChosenAgent()

		elif symbol == pyglet.window.key.W:
			self.worldMode = "Wandering"
			for agent in self.agents:
				agent.mode = "Wandering"
    
		elif symbol == pyglet.window.key.C:
			self.worldMode = "Cohesion"
			for agent in self.agents:
				agent.mode = "Cohesion"
    
		elif symbol == pyglet.window.key.S:
			self.worldMode = "Separation"
			for agent in self.agents:
				agent.mode = "Separation"
    
		elif symbol == pyglet.window.key.L:
			self.worldMode = "Alignment"
			for agent in self.agents:
				agent.mode = "Alignment"
    
		elif symbol == pyglet.window.key._1:
			self.agents[self.chosenIndex].increaseNearRange()
   
		elif symbol == pyglet.window.key._2:
			self.agents[self.chosenIndex].decreaseNearRange()
   
		elif symbol == pyglet.window.key._3:
			self.agents[self.chosenIndex].increaseFarRange()
   
		elif symbol == pyglet.window.key._4:
			self.agents[self.chosenIndex].decreaseFarRange()
			
    
	def updateChosenAgent(self):
		for i in range(0, len(self.agents)):
			self.agents[i].isChosen = (i == self.chosenIndex)