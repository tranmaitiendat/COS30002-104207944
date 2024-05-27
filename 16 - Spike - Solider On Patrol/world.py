'''A 2d world that supports agents with steering behaviour

Created for COS30002 AI for Games, by Clinton Woodward <cwoodward@swin.edu.au>
For class use only. Do not publically share or post this code without permission.

'''

from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from graphics import COLOUR_NAMES, window
from agent import Agent, Hunter, Prey, AGENT_MODES  # Agent with seek, arrive, flee and pursuit

class World(object):
	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
  
		self.preys = [Prey(self)]
		self.hunter = Hunter(self)
  
		self.paused = True
		self.showinfo = True
		self.target = pyglet.shapes.Star(
			cx / 2, cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main")
		)

	def update(self, delta):
		if not self.paused:
			
			self.hunter.update(delta)
			for projectile in self.hunter.projectiles:
				projectile.update(delta)
			for prey in self.preys:
				prey.update(delta)
   
			window._update_label('hunter mode', "Hunter's FSM mode: {}".format(self.hunter.mode))
			currentHealth = self.averagePreysHealth()
			maxHealth = self.preys[0].maxHealth
			window._update_label("prey health", f"Average Preys' health: {currentHealth:.2f}/{maxHealth:.2f}")
   
			if self.hunter.mode == "patrol":
				window._update_label('hunter state', "Hunter's visit type: {}".format(self.hunter.FSM.currentState()))
				window._update_label('hunter travelled', "Hunter's travelled distance: {}".format((int)(self.hunter.travelledDistance), ".2f"))
			else:
				window._update_label('hunter state', "Hunter's shooting mode: {}".format(self.hunter.FSM.currentState()))
				window._update_label('hunter travelled', "")

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
		if button == 1:
			self.target.x = x
			self.target.y = y
	
	def input_keyboard(self, symbol, modifiers):
    
		if symbol == pyglet.window.key.P:
			self.paused = not self.paused
   
		elif symbol == pyglet.window.key.A:
			self.preys.append(Prey(self))
   
		elif symbol in AGENT_MODES:
			
			self.hunter.mode = AGENT_MODES[symbol]
			self.hunter.FSM.mode = self.hunter.mode
   
		elif symbol == pyglet.window.key.R:

			self.hunter.randomise_path()
   
	def averagePreysHealth(self):
		sum = 0.
		for prey in self.preys:
			sum += prey.health

		sum /= len(self.preys)

		return sum
			
			
		