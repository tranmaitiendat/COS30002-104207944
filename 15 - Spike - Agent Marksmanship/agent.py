import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, window

class Agent(object):
    
    def __init__(self, world=None, scale=10.0, mass=1.0, color='ORANGE'):
        
        self.world = world
        
        dir = radians(random()*360)
        
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  
        self.acceleration = Vector2D()  
        self.mass = mass
        
        self.max_speed = scale * 10
        
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

        ### wander details
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        # Force and speed limiting code
        self.max_speed = 20.0 * scale
        self.max_force = 500.0
 
    def calculate(self, delta):
        
        raise NotImplementedError("This method should be overridden.")
        
    def update(self, delta):
        
        self.acceleration = self.calculate(delta) / self.mass
        
        # new velocity
        self.vel += self.acceleration * delta
        # check for limits of new velocity
        #self.vel.truncate(self.max_speed)
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
    
    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)
    
    def flee(self, other):
        from_target = self.pos - other.pos

        desiredVel = from_target.normalise() * self.max_speed
        return (desiredVel - self.vel) * 20
    
    def wander(self, delta):
        ''' random wandering using a projected jitter circle '''
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
        # and steer towards it

        return self.seek(world_target)
    
class Prey(Agent):
    
    def __init__(self, world=None, scale=10.0, mass=1.0, color='ORANGE'):
        
        super().__init__(world, scale, mass, color)
        
        self.collisionRange = 15
        
        self.maxHealth = 100
        self.health = self.maxHealth
        
        self.collisionRangeCircle = pyglet.shapes.Arc(
            x=self.pos.x, y=self.pos.y,
            radius=self.collisionRange,
            color=COLOUR_NAMES[self.color],
            batch=window.get_batch("main")
        )
        
        self.target = "First"
        
        self.firstTargetPos = Vector2D(x=200, y=600)
        self.secondTargetPos = Vector2D(x=900, y=600)
        
        self.pos = (self.firstTargetPos + self.secondTargetPos) / 2
        
        self.firstTarget = pyglet.shapes.Star(
			self.firstTargetPos.x, self.firstTargetPos.y, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main")
		)
        
        self.secondTarget = pyglet.shapes.Star(
			self.secondTargetPos.x, self.secondTargetPos.y, 
			30, 1, 4, 
			color=COLOUR_NAMES['BLUE'], 
			batch=window.get_batch("main")
		)
        
        # self.acceleration = self.seek(self.firstTargetPos)
        
    def updateFirstTargetPos(self, x, y):
        
        distanceBetweenNewTargets = (self.secondTargetPos - Vector2D(x=x, y=y)).length()

        if distanceBetweenNewTargets >= 100:        
            self.firstTargetPos.x = x
            self.firstTargetPos.y = y
            
            self.firstTarget.x = x
            self.firstTarget.y = y
        
    def updateSecondTargetPos(self, x, y):
        
        distanceBetweenNewTargets = (self.firstTargetPos - Vector2D(x=x, y=y)).length()
        
        if distanceBetweenNewTargets >= 100:  
            self.secondTargetPos.x = x
            self.secondTargetPos.y = y
            
            self.secondTarget.x = x
            self.secondTarget.y = y
        
    def calculate(self, delta):
        
        distanceToFirstTarget = (self.firstTargetPos - self.pos).length()
        distanceToSecondTarget = (self.secondTargetPos - self.pos).length()
        
        accel = self.acceleration
        
        if self.target == "First":
            accel = self.seek(self.firstTargetPos)
        elif self.target == "Second":
            accel = self.seek(self.secondTargetPos)
        
        if distanceToFirstTarget < self.collisionRange:
            self.target = "Second"
            
        elif distanceToSecondTarget < self.collisionRange:
            self.target = "First"
                
        self.acceleration = accel
        
        return accel
        
    def update(self, delta):
        
        super().update(delta)
        
        # Update the collision range renderables
        self.collisionRangeCircle.x = self.pos.x
        self.collisionRangeCircle.y = self.pos.y
            
class Hunter(Agent):
    
    def __init__(self, world=None, mass=1.0, color='DARK_GREEN'):
        
        super().__init__(world, 0, mass, color)
        
        self.mode = "Rifle"
        
        self.projectile = None
        
        self.pos = Vector2D(self.world.cx / 2, 100.)
        self.heading = Vector2D(0., 1.)
        
    def projectileSpeed(self):
        if self.mode == "Rifle" or self.mode == "Hand Gun":
            return 2.
        elif self.mode == "Rocket" or self.mode == "Hand Grenade":
            return 1
        
    def projectilePower(self):
        if self.mode == "Rifle":
            return 1.
        elif self.mode == "Rocket":
            return 5.
        elif self.mode == "Hand Gun":
            return 10.
        elif self.mode == "Hand Grenade":
            return 15.
        
    def inaccurateAngleRate(self):
        if self.mode == "Rifle" or self.mode == "Rocket":
            return 0.
        elif self.mode == "Hand Gun" or self.mode == "Hand Grenade":
            return 0.5
        
    def calculate(self, delta):
        
        accel = self.attack()
        
        self.acceleration = accel
        
        return accel
    
    def attack(self):
        
        prey = self.world.prey
        
        # return (prey.pos + speed * prey.vel - self.pos) / speed
        # Given p and o is the prey and projectile.
        # After a period of time "t", position of the prey and projectile will be:
        # pos_p(t) = pos_p + vel_p * t + (1/2)acc_p * t^2
        # pos_o(t) = pos_o + vel_o * t + (1/2)acc_o * t^2
        # We need to calculate where pos_p(t) = pos_o(t)
        # or pos_p + vel_p * t + (1/2)acc_p * t^2 = pos_o + vel_o * t + (1/2)acc_o * t^2
        # or 2 * pos_p + 2 * vel_p * t + acc_p * t^2 = 2 * pos_o + 2 * vel_o * t + acc_o * t^2
        # or acc_o * t^2 = 2(pos_p - pos_o) + 2t(vel_p - vel_o) + acc_p * t^2
        # or acc_o = (2(pos_p - pos_o) + 2t(vel_p - vel_o) + acc_p * t^2) / t^2
        
        # If the speed of the projectile is fast, the time to collide "t" is much shorter and vise versa
        timeToCollide = 1. / self.projectileSpeed()
        
        return (2 * (prey.pos - self.pos) + 2 * timeToCollide * (prey.vel - self.vel) + prey.acceleration * timeToCollide * timeToCollide) / (timeToCollide * timeToCollide)
    
    def shoot(self):
        
        if not self.projectile:
            self.projectile = Projectile(self.world, self.color, self.inaccurateAngleRate(), self.pos.x, self.pos.y, self.attack())  
            
    def update(self, delta):
        
        self.calculate(delta)
        
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)
        # update the vehicle render position
        self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
        self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
        self.vehicle.rotation = -self.heading.angle_degrees()

        if self.projectile:
            self.projectile.update(delta)
            
            distanceFromPreyToProjectile = (self.world.prey.pos - self.projectile.pos).length()
            if distanceFromPreyToProjectile <= self.world.prey.collisionRange:
                self.world.prey.health = max(0, self.world.prey.health - self.projectilePower())
                self.projectile = None
            
            elif self.projectile.pos.x > self.world.cx or self.projectile.pos.x < 0 or self.projectile.pos.y > self.world.cy or self.projectile.pos.y < 0:
                self.projectile = None

    
class Projectile(Agent):
    
    def __init__(self, world=None, color='GREEN', inaccurateAngleRate=0.1, x=0., y=0., accel=Vector2D()):
        
        super().__init__(world, 5., 1.0, color)
        
        self.inaccurateAngleRate = inaccurateAngleRate
        
        self.pos = Vector2D(x=x, y=y)
        
        self.acceleration = accel
        
        self.vehicle = pyglet.shapes.Circle(
            x=self.pos.x, y=self.pos.y,
            radius=10.0,
            color=COLOUR_NAMES[self.color],
            batch=window.get_batch("main")
        )
        
    def calculate(self):
        
        raise ValueError("This should not be called.")
        
    def update(self, delta):
        
        # new velocity
        self.vel += self.acceleration * delta
        
        # Slightly rotate velocity if the mode is Hand gun or hand generade
        # To rotate the a vector(x, y) by an angle alpha to become new vector (x', y'), we have the formula:
        # x' = x * cos(alpha) - y * sin(alpha)
        # y' = x * sin(alpha) + y * cos(alpha)
        newVelX = self.vel.x * cos(self.inaccurateAngleRate * delta) - self.vel.y * sin(self.inaccurateAngleRate * delta)
        newVelY = self.vel.y * sin(self.inaccurateAngleRate * delta) + self.vel.y * cos(self.inaccurateAngleRate * delta)
        self.vel = Vector2D(newVelX, newVelY)
        
        # update position
        self.pos += self.vel * delta
        # update heading is non-zero velocity (moving)
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()      

        self.vehicle.x = self.pos.x
        self.vehicle.y = self.pos.y
