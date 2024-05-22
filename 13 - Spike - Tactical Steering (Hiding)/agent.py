import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, ArrowLine, window

class Agent(object):
    
    def __init__(self, world=None, scale=30.0, mass=1.0, color='ORANGE'):
        
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
            Point2D(-10,  6),
            Point2D( 10,  0),
            Point2D(-10, -6)
        ]
        
        self.vehicle = pyglet.shapes.Triangle(
            self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
            self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
            self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
            color= COLOUR_NAMES[self.color],
            batch=window.get_batch("main")
        )
       
    def increaseMass(self):
        
        self.mass += 0.1
        
        print("New mass: {}".format(self.mass, ".2f"))
        
    def decreaseMass(self):
        
        if mass > 0.2:
            self.mass -= 0.1
        
        print("New mass: {}".format(self.mass, ".2f"))

    def increaseMaxSpeed(self):
        
        self.max_speed += 100.0
        
        print("New Max Speed: {}".format(self.max_speed, ".2f"))
        
    def decreaseMaxSpeed(self):
        
        if self.max_speed > 200.0:
            self.max_speed -= 100.0
        
        print("New Max Speed: {}".format(self.max_speed, ".2f"))       
 
    def calculate(self, delta):
        
        raise NotImplementedError("This method should be overridden.")
        
    def update(self, delta):
        
        acceleration = self.calculate(delta) / self.mass
        
        # new velocity
        self.vel += acceleration * delta
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
        self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
        self.vehicle.rotation = -self.heading.angle_degrees()

    def speed(self):
        return self.vel.length()
    
    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)
    
    def nearObstacle(self):
        for obstacle in self.world.obstacles:
            if self.agentIsNearAParticularObstacle(obstacle):
                return obstacle
            
        return None
            
    def agentIsNearAParticularObstacle(self, obstacle):
        from_target = self.pos - obstacle.pos
        distance = from_target.length()
        panicDistance = obstacle.radius + 20.0
        
        return distance < panicDistance
    
    def flee(self, obstacle):
        from_target = self.pos - obstacle.pos

        desiredVel = from_target.normalise() * self.max_speed
        return (desiredVel - self.vel)
    
class Prey(Agent):
    
    def __init__(self, world=None, scale=30.0, mass=1.0, color='ORANGE'):
        
        super().__init__(world, scale, mass, color)
        
        self.status = "Idle"
        
    def calculate(self, delta):
        
        if not self.isPanic():
            
            self.status = "Idle"
            
            target_pos = self.pos
            
        else:
            
            self.status = "Hiding"
            
            safestObject = self.safestObject()
            safestObjectPos = safestObject.pos
            
            # Vector from prey to Safest Object
            toSafestObjectPos = safestObjectPos - self.pos
            
            # Determine the vector position behind that Safest Object 
            toBehindsafestObjectPos = toSafestObjectPos.copy().normalise() * (sqrt(toSafestObjectPos.copy().x * toSafestObjectPos.copy().x + toSafestObjectPos.copy().y * toSafestObjectPos.copy().y) + 10.0 + safestObject.radius)
            
            # Determine the position behind that Safest Object
            behindsafestObjectPos = toBehindsafestObjectPos + self.pos
                
            target_pos = behindsafestObjectPos
            
            # Emphasize target safest planet as color of red
            for obstacle in self.world.obstacles:
                obstacle.target.color = COLOUR_NAMES['TRANSPARENT']
                obstacle.circleEmphasize.color = COLOUR_NAMES['TRANSPARENT']
                
            safestObject.color = COLOUR_NAMES[self.color]
            safestObject.target.color = COLOUR_NAMES[self.color]
            safestObject.circleEmphasize.color = COLOUR_NAMES[self.color]
            safestObject.target.x = target_pos.x
            safestObject.target.y = target_pos.y
            
            
        accel = self.seek(target_pos)
        
        # Flee the near obstacle
        nearObstacle = self.nearObstacle()
        
        if nearObstacle:
            accel = self.flee(nearObstacle)
        
        self.acceleration = accel
        
        return accel
    
    def safestObject(self):
        # Is most far from the Hunter
        
        maxDistance = -float('inf')
        currentNearestObject = self.world.obstacles[0]
        
        
        for obstacle in self.world.obstacles:
            
            if obstacle.isSafe():
                
                from_target = self.world.hunter.pos - obstacle.pos
                distance = from_target.length()
                
                if distance > maxDistance:
                    maxDistance = distance
                    currentNearestObject = obstacle
                
        return currentNearestObject
        
    def isPanic(self):
        
        hunter = self.world.hunter
        
        panicDistance = 200
        
        from_hunter = self.pos - hunter.pos
        distanceToHunter = from_hunter.length()
        
        return distanceToHunter < panicDistance   
    
class Hunter(Agent):
    
    def __init__(self, world=None, scale=20.0, mass=3.0, color='RED'):
        
        super().__init__(world, scale, mass, color)
        
        self.status = "Wandering"
        
		# wander info render objects
        self.info_wander_circle = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['WHITE'], batch=window.get_batch("info"))
        self.info_wander_target = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['GREEN'], batch=window.get_batch("info"))
		# add some handy debug drawing info lines - force and velocity
        self.info_force_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['BLUE'], batch=window.get_batch("info"))
        self.info_vel_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['AQUA'], batch=window.get_batch("info"))
        self.info_net_vectors = [
            ArrowLine(
                Vector2D(0,0), 
                Vector2D(0,0), 
                colour=COLOUR_NAMES['GREY'], 
                batch=window.get_batch("info")
            ),
            ArrowLine(
                Vector2D(0,0), 
                Vector2D(0,0), 
                colour=COLOUR_NAMES['GREY'], 
                batch=window.get_batch("info")
            ),
        ]

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
        
        if self.distanceToPrey() < 250:
            self.status = "Chasing"
            target_pos = self.world.prey.pos
            
            accel = self.seek(target_pos)
        else:
            self.status = "Wandering"
            
            accel = self.wander(delta)
        
        # Flee the near obstacle
        nearObstacle = self.nearObstacle()
        
        if nearObstacle:
            accel = self.flee(nearObstacle)
        
        self.acceleration = accel
        
        return accel
    
    def distanceToPrey(self):
        
        prey = self.world.prey
        
        from_prey = self.pos - prey.pos
        distanceToPrey = from_prey.length()
        
        return distanceToPrey 
    
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
        # set the position of the Agent’s debug circle to match the vectors we’ve created
        circle_pos = self.world.transform_point(wander_dist_vector, self.pos, self.heading, self.side,)
        self.info_wander_circle.x = circle_pos.x
        self.info_wander_circle.y = circle_pos.y
        self.info_wander_circle.radius = self.wander_radius
        # project the target into world space
        world_target = self.world.transform_point(target, self.pos, self.heading, self.side)
        #set the target debug circle position
        self.info_wander_target.x = world_target.x
        self.info_wander_target.y = world_target.y
        # and steer towards it

        return self.seek(world_target)
 