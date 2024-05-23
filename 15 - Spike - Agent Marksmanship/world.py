'''A 2d world that supports preys with steering behaviour

Created for COS30002 AI for Games, by Clinton Woodward <cwoodward@swin.edu.au>
For class use only. Do not publically share or post this code without permission.

'''

from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from graphics import COLOUR_NAMES, window
from agent import Agent, Prey, Hunter

class World(object):
	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
  
		self.prey = Prey(self)
  
		self.hunter = Hunter(self)
  
		self.paused = False
		self.showinfo = True

	def update(self, delta):
     
		if not self.paused:

			self.prey.update(delta)
    
			window._update_label("prey collision range", "Prey's collision range: {}".format(self.prey.collisionRange))	
			window._update_label("prey health", "Prey's health: {}/{}".format(self.prey.health, self.prey.maxHealth))	
			window._update_label("prey first target", "Prey's first target: {}".format(self.prey.firstTargetPos))	
			window._update_label("prey second target", "Prey's second target: {}".format(self.prey.secondTargetPos))
   
			self.hunter.update(delta)	
			window._update_label("hunter mode", "Hunter's projectile mode: {}".format(self.hunter.mode))
			window._update_label("inaccurate rate", "Inaccurate angle rate: {} degree".format(self.hunter.inaccurateAngleRate()))
			window._update_label("eta time to collide", "Estimate time to collide: {}s".format(1. / self.hunter.projectileSpeed()))
   
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

	def input_mouse(self, x, y, button, modifiers):
		if button == pyglet.window.mouse.LEFT:  # left
			self.prey.updateFirstTargetPos(x, y)
		elif button == pyglet.window.mouse.RIGHT:
			self.prey.updateSecondTargetPos(x, y)
	
	def input_keyboard(self, symbol, modifiers):
     
		if symbol == pyglet.window.key.P:
			self.paused = not self.paused
   
		elif symbol == pyglet.window.key.SPACE:
			self.hunter.shoot()

		elif symbol == pyglet.window.key.R: 
			self.hunter.mode = "Rifle"
   
		elif symbol == pyglet.window.key.T: 
			self.hunter.mode = "Rocket"
   
		elif symbol == pyglet.window.key.G: 
			self.hunter.mode = "Hand Gun"
   
		elif symbol == pyglet.window.key.H: 
			self.hunter.mode = "Hand Grenade"
