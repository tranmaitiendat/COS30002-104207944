'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by 
	Clinton Woodward <cwoodward@swin.edu.au>
	James Bonner <jbonner@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''
import pyglet
from vector2d import Vector2D
from point2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from path import Path

AGENT_MODES = {
	pyglet.window.key._1: 'patrol',
	pyglet.window.key._2: 'attack',
}

class Agent(object):

	# NOTE: Class Object (not *instance*) variables!
	DECELERATION_SPEEDS = {
		'slow': 0.9,
		'normal': 0.8,
		'fast': 0.6,
	}

	def __init__(self, world=None, scale=20.0, mass=1.0, color="ORANGE"):
		# keep a reference to the world object
		self.world = world
		
		dir = radians(random()*360)
  
		self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
		self.vel = Vector2D()
  
		self.heading = Vector2D(sin(dir), cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale, scale)  # easy scaling of agent size
		self.acceleration = Vector2D() # current acceleration due to force
		self.mass = mass

		# data for drawing this agent
		self.color = color
		self.vehicle_shape = [
			Point2D((-sqrt(3) / 6) * 20,  5),
			Point2D((sqrt(3) / 3) * 20,  0),
			Point2D((-sqrt(3) / 6) * 20,  -5),
		]
		
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
			color= COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)
  
		# Force and speed limiting code
		self.max_speed = 20.0 * scale

	def calculate(self, delta):

		raise NotImplementedError("This method should be overridden.")

	def update(self, delta):

		self.acceleration = self.calculate(delta) / self.mass
		
		# new velocity
		self.vel += self.acceleration * delta
		# check for limits of new velocity
		self.vel.truncate(self.max_speed)
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		# treat world as continuous space - wrap new position if needed
		self.world.wrap_around(self.pos)
		# update the vehicle render position
		self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
		self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
		self.vehicle.rotation = -self.heading.angle_degrees()
  
	def speed(self):
		return self.vel.length()

	#--------------------------------------------------------------------------

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)

class Hunter(Agent):
	
	def __init__(self, world=None, scale=20.0, mass=1.0, color='RED', mode='patrol'):
		
		super().__init__(world, scale, mass, color=color)
		
		self.vehicle_shape = [
			Point2D((-sqrt(3) / 6) * 30,  10),
			Point2D((sqrt(3) / 3) * 30,  0),
			Point2D((-sqrt(3) / 6) * 30,  -10),
		]
		
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
			color= COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)

		self.mode = mode
		
		self.path = Path()
		self.randomise_path()
		self.waypoint_threshold = 2.0
  
		self.travelledDistance = 0.
  
		self.FSM = FSM(self)
  
		self.projectiles = []
  
	def calculate(self, delta):
	 
		targetPos = Vector2D(self.world.target.x, self.world.target.y)
		
		accel = Vector2D()

		
		if self.mode == "patrol":
			accel = self.FSM.run(targetPos)
		elif self.mode == "attack":
			accel = Vector2D()
			self.vel = Vector2D()
   
			self.FSM.run(targetPos)
		
		self.acceleration = accel
		
		return accel

	def update(self, delta):
	 
		self.acceleration = self.calculate(delta) / self.mass
		
		# new velocity
		self.vel += self.acceleration * delta
		# check for limits of new velocity
		self.vel.truncate(self.max_speed)
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		# treat world as continuous space - wrap new position if needed
		self.world.wrap_around(self.pos)
		# update the vehicle render position
		self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
		self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
		self.vehicle.rotation = -self.heading.angle_degrees()
  
		self.travelledDistance += (self.vel * delta).copy().length()
  
		# Update the deletability of projectiles
		i = 0
		while i < len(self.projectiles):

			# Find the nearest prey
			nearestPrey = None
			distanceToNearestPrey = float('inf')
			for prey in self.world.preys:
				distanceToPrey = (self.projectiles[i].pos - prey.pos).length()
				if distanceToPrey < distanceToNearestPrey:
					nearestPrey = prey
					distanceToNearestPrey = distanceToPrey

			# Collide with the prey
			if distanceToNearestPrey < nearestPrey.collisionRange:
				nearestPrey.health = max(0., nearestPrey.health - 10)
				del self.projectiles[i]
			# Out of the map
			elif self.projectiles[i].pos.x > self.world.cx or self.projectiles[i].pos.x < 0 or self.projectiles[i].pos.y > self.world.cy or self.projectiles[i].pos.y < 0:
				del self.projectiles[i]
			else:
				i += 1
  
		self.path.renderable.draw()
  
	def randomise_path(self):
		cx = 640  # width
		cy = 360  # height
		
		min_dist = 15  # the minimum distance between the waypoints
		
		minx = cx * 0.75
		miny = cy * 0.75
		
		maxx = cx * 1
		maxy = cy * 1
		
		self.path.create_random_path(min_dist, minx, miny, maxx, maxy)
		
	def followPath(self, decelerationType="arrive slowly"):
		# If heading to final point (is_finished?), return a slow down force vector (Arrive)
		if self.path.is_finished():
			return self.arrive_slow(self.path._pts[-1])
		else:
			distance_to_way_point = self.pos.distance(self.path.current_pt())
			# If within threshold distance of current way point, inc to next in path
			if distance_to_way_point <= self.waypoint_threshold:
				self.path.inc_current_pt()
	
			if decelerationType == "seek":
				return self.seek(self.path.current_pt())
			elif decelerationType == "arrive slowly":
				return self.arriveSlow(self.path.current_pt())
			elif decelerationType == "arrive normaly":
				return self.arriveNormal(self.path.current_pt())
			else:
				return self.arriveFast(self.path.current_pt())

	def arriveSlow(self, target_pos):

		decel_rate = self.DECELERATION_SPEEDS["slow"]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)

	def arriveNormal(self, target_pos):

		decel_rate = self.DECELERATION_SPEEDS["normal"]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)

	def arriveFast(self, target_pos):

		decel_rate = self.DECELERATION_SPEEDS["fast"]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)

class Prey(Agent):
	
	def __init__(self, world=None, scale=1.0, mass=1.0):
		
		super().__init__(world, scale, mass)
  
		self.collisionRange = 15
		
		self.maxHealth = 100
		self.health = self.maxHealth
		
		self.collisionRangeCircle = pyglet.shapes.Arc(
			x=self.pos.x, y=self.pos.y,
			radius=self.collisionRange,
			color=COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)
  
		### wander details
		self.wander_target = Vector2D(1, 0)
		self.wander_dist = 1.0 * scale
		self.wander_radius = 1.0 * scale
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
  
	def calculate(self, delta):
	 
		accel = self.wander(delta)

		self.acceleration = accel
		
		return accel
  
	def update(self, delta):

		super().update(delta)
  
		# Update the collision range renderables
		self.collisionRangeCircle.x = self.pos.x
		self.collisionRangeCircle.y = self.pos.y
  
		if self.health <= 0.:
			self.collisionRange = 0.
			self.collisionRangeCircle.color = COLOUR_NAMES["TRANSPARENT"]
			self.vehicle.color = COLOUR_NAMES["TRANSPARENT"]
  
	def wander(self, delta):

		wander_target = self.wander_target
		# this behaviour is dependent on the update rate, so this line must
		# be included when using time independent framerate.
		jitter = self.wander_jitter * delta # this time slice
		# first, add a small random vector to the target's position
		wander_target += Vector2D(uniform(-1,1) * jitter, uniform(-1,1) * jitter)
		# re-project this new vector back on to a unit circle
		wander_target.normalise()
		# increase the length of the vector to the same as the radius
		# of the wander circle
		wander_target *= self.wander_radius
		# move the target into a position wander_dist in front of the agent
		wander_dist_vector = Vector2D(self.wander_dist, 0) #also used for rendering
		target = wander_target + Vector2D(self.wander_dist, 0)

		# project the target into world space
		world_target = self.world.transform_point(target, self.pos, self.heading, self.side)

		return self.seek(world_target)

class Projectile(Agent):
	
	def __init__(self, world=None, color='GREEN', x=0., y=0., accel=Vector2D()):
		
		super().__init__(world, 5., 1.0, color)
		
		self.pos = Vector2D(x=x, y=y)
		
		self.acceleration = accel
		
		self.vehicle = pyglet.shapes.Circle(
			x=self.pos.x, y=self.pos.y,
			radius=5.0,
			color=COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)
  
	def calculate(self):
		
		raise ValueError("This should not be called.")
		
	def update(self, delta):
		
		# new velocity
		self.vel += self.acceleration * delta
		
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()	  

		self.vehicle.x = self.pos.x
		self.vehicle.y = self.pos.y

class FSM:
	
	def __init__(self, hunter):
		
		self.hunter = hunter
		
		self.mode = self.hunter.mode

		self.firstModeStates = ["seek", "arrive slowly", "arrive normally", "arrive fast"]
		self.secondModeStates = ["shoot normally", "shoot doubly", "shoot spreadly", "shoot massively spreadly"]
  
		self.secondModeStates = self.secondModeStates[::-1]
		
		self.stateIndex = 0
		
	def currentState(self):
	 
		self.mode = self.hunter.mode
	
		if self.mode == "patrol":
			self.stateIndex = (int)(self.hunter.travelledDistance / 200) % 4
   
			return self.firstModeStates[self.stateIndex]
		
		else:
			averagePreyHealthRemainingRate = 1. - (self.hunter.world.averagePreysHealth() / self.hunter.world.preys[0].maxHealth)
   
			self.stateIndex = (int)(averagePreyHealthRemainingRate * 4) % 4
   
			return self.secondModeStates[self.stateIndex]
	
	def run(self, targetPos):

		self.mode = self.hunter.mode
	
		if self.mode == "patrol":
			self.stateIndex = (int)(self.hunter.travelledDistance / 200) % 4
			
			return self.hunter.followPath(self.firstModeStates[self.stateIndex])
		
		elif self.mode == "attack":
			averagePreyHealthRemainingRate = 1. - (self.hunter.world.averagePreysHealth() / self.hunter.world.preys[0].maxHealth)
   
			self.stateIndex = (int)(averagePreyHealthRemainingRate * 4) % 4
   
			projectileAcceleration = targetPos - self.hunter.pos
   
			if len(self.hunter.projectiles) < 1:
				if self.currentState() == "shoot normally":
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, projectileAcceleration.copy().normalise() * 1000.))

				elif self.currentState() == "shoot doubly":
					
					# Calculte a position behind the current position of the hunter, so that the two projectiles seem to be shooted continuosly
					behindPos = self.hunter.pos - projectileAcceleration.copy().normalise() * 15.
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, projectileAcceleration.copy().normalise() * 1000.))
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, behindPos.x, behindPos.y, projectileAcceleration.copy().normalise() * 1000.))

				elif self.currentState() == "shoot spreadly":
					
					# -pi/12 rad (-15 deg)
					rotateProjectileAccelerationLeft = Vector2D()
					rotateProjectileAccelerationLeft.x = projectileAcceleration.x * cos(-3.14 / 12.) - projectileAcceleration.y * sin(-3.14 / 12.)
					rotateProjectileAccelerationLeft.y = projectileAcceleration.y * sin(-3.14 / 12.) + projectileAcceleration.y * cos(-3.14 / 12.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, rotateProjectileAccelerationLeft.copy().normalise() * 1000.))
     
					# pi/12 rad (15 deg)
					rotateProjectileAccelerationRight = Vector2D()
					rotateProjectileAccelerationRight.x = projectileAcceleration.x * cos(3.14 / 12.) - projectileAcceleration.y * sin(3.14 / 12.)
					rotateProjectileAccelerationRight.y = projectileAcceleration.y * sin(3.14 / 12.) + projectileAcceleration.y * cos(3.14 / 12.)

					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, rotateProjectileAccelerationRight.copy().normalise() * 1000.))
     
					# 0 rad accel
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, projectileAcceleration.copy().normalise() * 1000.))
     
				else:
     
					# -pi/6 rad (-30 deg)
					firstRotateProjectileAcceleration = Vector2D()
					firstRotateProjectileAcceleration.x = projectileAcceleration.x * cos(-3.14 / 6.) - projectileAcceleration.y * sin(-3.14 / 6.)
					firstRotateProjectileAcceleration.y = projectileAcceleration.y * sin(-3.14 / 6.) + projectileAcceleration.y * cos(-3.14 / 6.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, firstRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# pi/6 rad (30 deg)
					secondRotateProjectileAcceleration = Vector2D()
					secondRotateProjectileAcceleration.x = projectileAcceleration.x * cos(3.14 / 6.) - projectileAcceleration.y * sin(3.14 / 6.)
					secondRotateProjectileAcceleration.y = projectileAcceleration.y * sin(3.14 / 6.) + projectileAcceleration.y * cos(3.14 / 6.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, secondRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# -pi/3 rad (-60 deg)
					thirdRotateProjectileAcceleration = Vector2D()
					thirdRotateProjectileAcceleration.x = projectileAcceleration.x * cos(-3.14 / 3.) - projectileAcceleration.y * sin(-3.14 / 3.)
					thirdRotateProjectileAcceleration.y = projectileAcceleration.y * sin(-3.14 / 3.) + projectileAcceleration.y * cos(-3.14 / 3.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, thirdRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# pi/3 rad (60 deg)
					fourthRotateProjectileAcceleration = Vector2D()
					fourthRotateProjectileAcceleration.x = projectileAcceleration.x * cos(3.14 / 3.) - projectileAcceleration.y * sin(3.14 / 3.)
					fourthRotateProjectileAcceleration.y = projectileAcceleration.y * sin(3.14 / 3.) + projectileAcceleration.y * cos(3.14 / 3.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, fourthRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# -pi/2 rad (-90 deg)
					fifthRotateProjectileAcceleration = Vector2D()
					fifthRotateProjectileAcceleration.x = projectileAcceleration.x * cos(-3.14 / 2.) - projectileAcceleration.y * sin(-3.14 / 2.)
					fifthRotateProjectileAcceleration.y = projectileAcceleration.y * sin(-3.14 / 2.) + projectileAcceleration.y * cos(-3.14 / 2.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, fifthRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# pi/2 rad (90 deg)
					sixthRotateProjectileAcceleration = Vector2D()
					sixthRotateProjectileAcceleration.x = projectileAcceleration.x * cos(3.14 / 2.) - projectileAcceleration.y * sin(3.14 / 2.)
					sixthRotateProjectileAcceleration.y = projectileAcceleration.y * sin(3.14 / 2.) + projectileAcceleration.y * cos(3.14 / 2.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, sixthRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# -2pi/3 rad (-120 deg)
					seventhRotateProjectileAcceleration = Vector2D()
					seventhRotateProjectileAcceleration.x = projectileAcceleration.x * cos(-3.14 * 2. / 3.) - projectileAcceleration.y * sin(-3.14 * 2. / 3.)
					seventhRotateProjectileAcceleration.y = projectileAcceleration.y * sin(-3.14 * 2. / 3.) + projectileAcceleration.y * cos(-3.14 * 2. / 3.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, seventhRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# 2pi/3 rad (120 deg)
					eighthRotateProjectileAcceleration = Vector2D()
					eighthRotateProjectileAcceleration.x = projectileAcceleration.x * cos(3.14 * 2. / 3.) - projectileAcceleration.y * sin(3.14 * 2. / 3.)
					eighthRotateProjectileAcceleration.y = projectileAcceleration.y * sin(3.14 * 2. / 3.) + projectileAcceleration.y * cos(3.14 * 2. / 3.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, eighthRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# -5pi/6 rad (-150 deg)
					ninthRotateProjectileAcceleration = Vector2D()
					ninthRotateProjectileAcceleration.x = projectileAcceleration.x * cos(-3.14 * 5. / 6.) - projectileAcceleration.y * sin(-3.14 * 5. / 6.)
					ninthRotateProjectileAcceleration.y = projectileAcceleration.y * sin(-3.14 * 5. / 6.) + projectileAcceleration.y * cos(-3.14 * 5. / 6.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, ninthRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# 5pi/6 rad (150 deg)
					tenthRotateProjectileAcceleration = Vector2D()
					tenthRotateProjectileAcceleration.x = projectileAcceleration.x * cos(3.14 * 5. / 6.) - projectileAcceleration.y * sin(3.14 * 5. / 6.)
					tenthRotateProjectileAcceleration.y = projectileAcceleration.y * sin(3.14 * 5. / 6.) + projectileAcceleration.y * cos(3.14 * 5. / 6.)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, tenthRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# pi rad (180 deg)
					elventhRotateProjectileAcceleration = Vector2D()
					elventhRotateProjectileAcceleration.x = projectileAcceleration.x * cos(3.14) - projectileAcceleration.y * sin(3.14)
					elventhRotateProjectileAcceleration.y = projectileAcceleration.y * sin(3.14) + projectileAcceleration.y * cos(3.14)
     
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, elventhRotateProjectileAcceleration.copy().normalise() * 1000.))
     
					# 0 rad
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, projectileAcceleration.copy().normalise() * 1000.))
     

			